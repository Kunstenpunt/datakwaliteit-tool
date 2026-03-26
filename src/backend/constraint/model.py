from typing import Optional

from PySide6.QtCore import Signal, QObject


from .base import (
    Constraint,
    Property,
    ValidationMode,
    ValidationState,
)
from .queries import QueryBuilder
from .constraint_types import *
from ..utils import idFromUrl, stripUrlPartFromTable
from ..wikibasehelper import WikibaseConfig, WikibaseQueryRunner

# idee: eis dat alle entiteiten en properties die mappen op properties van wikidata hetzelfde label hebben in het Engels -> op die manier steeds correcte mapping


class ConstraintHelper(QObject):
    qualifiersUpdated = Signal()
    violationsUpdated = Signal()

    exceptionsUpdated = Signal()
    inputCountUpdated = Signal()
    validationStateUpdated = Signal()

    def __init__(
        self,
        queryBuilder: QueryBuilder,
        wikibaseConfig: WikibaseConfig,
        wikibaseQueryRunner: WikibaseQueryRunner,
    ) -> None:
        super().__init__()
        self.constraint: Optional[Constraint] = None

        self._queryBuilder = queryBuilder
        self._wikibaseConfig = wikibaseConfig
        self._wikibaseQueryRunner = wikibaseQueryRunner

    def queryInputCount(self, c: Constraint) -> None:
        query = self._queryBuilder.buildInputCountQuery(c)

        if query is None:
            print(f"Querying input count not implemented for {c}")
            return

        self._wikibaseQueryRunner.queueQueryForExecution(
            query, self._queryInputCountResult, c
        )

    def _queryInputCountResult(self) -> None:
        if not isinstance(self._wikibaseQueryRunner.callbackData, Constraint):
            return

        self.constraint = self._wikibaseQueryRunner.callbackData

        result = self._wikibaseQueryRunner.queryResult
        # This checks both if result is None or if result is empty list
        if not result:
            return

        try:
            self.constraint.inputCount = int(result[1][0])
        except:
            return
        self.inputCountUpdated.emit()

    def queryExceptions(self, c: Constraint) -> None:
        query = self._queryBuilder.buildExceptionIdsQuery(c)

        self._wikibaseQueryRunner.queueQueryForExecution(
            query, self._queryExceptionsResult, c
        )

    def _queryExceptionsResult(self) -> None:
        if not isinstance(self._wikibaseQueryRunner.callbackData, Constraint):
            return

        self.constraint = self._wikibaseQueryRunner.callbackData

        result = self._wikibaseQueryRunner.queryResult
        # This checks both if result is None or if result is empty list
        if not result:
            return

        resultStripped = stripUrlPartFromTable(
            self._wikibaseConfig.getBaseUrl(), result
        )
        try:
            self.constraint.exceptionIds = [row[0] for row in resultStripped[1:]]
        except:
            return

        self.exceptionsUpdated.emit()

    def queryQualifiers(self, c: Constraint) -> None:
        if c.qualifiersObtained:
            return

        query = self._queryBuilder.buildQualifiersQuery(c)
        if query is None:
            return

        self._wikibaseQueryRunner.queueQueryForExecution(
            query, self._queryQualifiersResult, c
        )

    def _queryQualifiersResult(self) -> None:
        if not isinstance(self._wikibaseQueryRunner.callbackData, Constraint):
            return

        self.constraint = self._wikibaseQueryRunner.callbackData

        result = self._wikibaseQueryRunner.queryResult
        # This checks both if result is None or if result is empty list
        if not result:
            self._updateValidationState(ValidationState.FAILED)
            return

        self.constraint.updateQualifiers(result)

        if self.constraint.qualifiersObtained:
            self.qualifiersUpdated.emit()
        else:
            self._updateValidationState(ValidationState.FAILED)
            return

        # if this qualifier query was a prerequisite of a validation query, continue with that validation
        if self.constraint.doValidation:
            self.queryViolations(self.constraint)

    def queryViolations(self, c: Constraint) -> None:
        self.constraint = c
        self._updateValidationState(ValidationState.VALIDATING)

        if not self.constraint.qualifiersObtained:
            self.constraint.doValidation = True
            self.queryQualifiers(self.constraint)
            return

        query = self._queryBuilder.buildViolationsQuery(self.constraint)
        if query is None:
            return

        self._wikibaseQueryRunner.queueQueryForExecution(
            query, self._queryViolationsResult, self.constraint
        )

    def _queryViolationsResult(self) -> None:
        if not isinstance(self._wikibaseQueryRunner.callbackData, Constraint):
            return

        self.constraint = self._wikibaseQueryRunner.callbackData

        result = self._wikibaseQueryRunner.queryResult
        if not result:
            self._updateValidationState(ValidationState.FAILED)
            return

        self.constraint.updateViolations(result)

        if self.constraint.violations is not None:
            self._updateValidationState(
                ValidationState.VALIDATED
                if self.constraint.validationMode == ValidationMode.NO_LIMIT
                else ValidationState.PARTIAL
            )
            self.violationsUpdated.emit()
        else:
            self._updateValidationState(ValidationState.FAILED)

    def _updateValidationState(self, validationState: ValidationState) -> None:
        if self.constraint is None:
            return

        if self.constraint.validationState != validationState:
            self.constraint.validationState = validationState
            self.validationStateUpdated.emit()


CONSTRAINT_MAP = {
    "single-value constraint": SingleValueConstraint,
    "value-type constraint": ValueTypeConstraint,
    "subject type constraint": SubjectTypeConstraint,
    "required qualifier constraint": RequiredQualifierConstraint,
    "allowed qualifiers constraint": AllowedQualifiersConstraint,
    "conflicts-with constraint": ConflictsWithConstraint,
    "distinct-values constraint": DistinctValuesConstraint,
    "format constraint": FormatConstraint,
    "item-requires-statement constraint": ItemRequiresStatementConstraint,
    "value-requires-statement constraint": ValueRequiresStatementConstraint,
}


class ConstraintCheckModel(QObject):

    constraintsUpdated = Signal()
    validationStateChanged = Signal()
    focusedConstraintUpdated = Signal()
    focusedConstraintInputCountUpdated = Signal()
    focusedConstraintQualifiersUpdated = Signal()
    focusedConstraintViolationsUpdated = Signal()
    validateAllDone = Signal()

    def __init__(
        self,
        queryBuilder: QueryBuilder,
        wikibaseConfig: WikibaseConfig,
        wikibaseQueryRunner: WikibaseQueryRunner,
    ) -> None:
        super().__init__()

        self._queryBuilder = queryBuilder
        self._wikibaseConfig = wikibaseConfig
        self._wikibaseQueryRunner = wikibaseQueryRunner

        self._constraintHelper = ConstraintHelper(
            self._queryBuilder,
            self._wikibaseConfig,
            self._wikibaseQueryRunner,
        )
        self._constraintHelper.inputCountUpdated.connect(self._onInputCountUpdated)
        self._constraintHelper.qualifiersUpdated.connect(self._onQualifiersUpdated)
        self._constraintHelper.violationsUpdated.connect(self._onViolationsUpdated)
        self._constraintHelper.validationStateUpdated.connect(self._validateNextInQueue)
        self._constraintHelper.validationStateUpdated.connect(
            self.validationStateChanged
        )

        self.constraints: dict[tuple[str, str], Constraint] = {}
        self.focusedConstraint: Optional[Constraint] = None
        self._validationQueue: list[Constraint] = []
        self._validatingQueue = False

    def updateConstraints(self) -> None:
        query = self._queryBuilder.buildConstrainedPropertiesQuery()
        self._wikibaseQueryRunner.queueQueryForExecution(
            query, self._updateConstraintsResult
        )

    def _updateConstraintsResult(self) -> None:
        result = self._wikibaseQueryRunner.queryResult
        if not result:
            return
        self.constraints = {}
        try:
            for [propId, propLabel, consId, consLabel] in result[1:]:
                propId = idFromUrl(propId)
                consId = idFromUrl(consId)
                constType = CONSTRAINT_MAP.get(consLabel)
                if constType is None:
                    constType = Constraint

                try:
                    constraint = constType(
                        consId,
                        consLabel,
                        Property(propId, propLabel),
                    )
                except ValueError:
                    print(f"Wrong IDs for property-constraint pair: {propId}-{consId}")
                    continue

                self.constraints[consId, propId] = constraint
        except:
            return

        self.constraintsUpdated.emit()

    def getConstraintsListFull(
        self,
    ) -> list[tuple[str, str, str, str, bool, ValidationState]]:
        return sorted(
            [
                (
                    c.property.identifier,
                    c.property.label,
                    c.identifier,
                    c.label,
                    c.implemented,
                    c.validationState,
                )
                for c in self.constraints.values()
            ]
        )

    def setFocusedConstraint(self, propId: str, constraintId: str) -> None:
        constraint = self.constraints.get((constraintId, propId))
        if constraint:
            self.focusedConstraint = constraint
            self.focusedConstraintUpdated.emit()
            self._constraintHelper.queryQualifiers(constraint)
            self._constraintHelper.queryInputCount(constraint)

    def validateFocusedConstraint(
        self,
        validationMode: ValidationMode,
        limit: int,
        page: int,
        sort: bool,
    ) -> None:
        if self.focusedConstraint is None:
            return

        self.focusedConstraint.validationMode = validationMode
        self.focusedConstraint.limit = limit
        self.focusedConstraint.page = page
        self.focusedConstraint.sort = sort
        if self._validatingQueue:
            self._validationQueue.append(self.focusedConstraint)
        else:
            self._constraintHelper.queryViolations(self.focusedConstraint)
            self._constraintHelper.queryExceptions(self.focusedConstraint)

    def validatingAll(self) -> bool:
        return len(self._validationQueue) != 0

    def stopValidatingAll(self) -> None:
        self._validationQueue = []
        self.validateAllDone.emit()

    def validateAll(self) -> None:
        self._validationQueue = list(self.constraints.values())
        self._validatingQueue = True
        self._validateNextInQueue()

    def _validateNextInQueue(self) -> None:
        c = self._constraintHelper.constraint
        if c is not None and c.validationState == ValidationState.VALIDATING:
            return

        if not self._validationQueue:
            self.validateAllDone.emit()
            self._validatingQueue = False
            return
        constraint = self._validationQueue[-1]
        if (
            constraint.implemented
            and constraint.validationState == ValidationState.UNVALIDATED
        ):
            self._validationQueue.pop()
            self._constraintHelper.queryViolations(constraint)
            self._constraintHelper.queryExceptions(constraint)
        else:
            self._validationQueue.pop()
            self._validateNextInQueue()

    def _onInputCountUpdated(self) -> None:
        c = self._constraintHelper.constraint
        if c == self.focusedConstraint:
            self.focusedConstraintInputCountUpdated.emit()

    def _onQualifiersUpdated(self) -> None:
        c = self._constraintHelper.constraint
        if c == self.focusedConstraint:
            self.focusedConstraintQualifiersUpdated.emit()

    def _onViolationsUpdated(self) -> None:
        c = self._constraintHelper.constraint
        if c == self.focusedConstraint:
            self.focusedConstraintViolationsUpdated.emit()
