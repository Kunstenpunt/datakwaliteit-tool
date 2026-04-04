from enum import StrEnum
from typing import Optional, Sequence

from PySide6.QtCore import Signal, QObject


from .base import (
    Constraint,
    Property,
    ValidationMode,
    ValidationState,
)
from .queries import QueryBuilder
from .constraint_types import *
from ..sql import SqlDatabase
from ..utils import idFromUrl, stripUrlPartFromTable
from ..wikibasehelper import WikibaseConfig, WikibaseQueryRunner

VIOLATION_ROW_ID_COLUMN = 0
VIOLATION_STATEMENT_COLUMN = 1
VIOLATION_ITEM_COLUMN = 2


class ConstraintsTableColumn(StrEnum):
    ROW_ID = "rowId"
    PROPERTY_IDENTIFIER = "propertyIdentifier"
    PROPERTY_LABEL = "propertyLabel"
    CONSTRAINT_IDENTIFIER = "constraintIdentifier"
    CONSTRAINT_LABEL = "constraintLabel"
    IMPLEMENTED = "implemented"
    VALIDATION_STATE = "validationState"


class ConstraintHelper(QObject):
    qualifiersUpdated = Signal()
    violationsUpdated = Signal(Constraint)

    exceptionsUpdated = Signal()
    inputCountUpdated = Signal()
    validationStateUpdated = Signal(Constraint)

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

        resultStripped = stripUrlPartFromTable(self._wikibaseConfig.baseUrl, result)
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
            self.violationsUpdated.emit(self.constraint)
        else:
            self._updateValidationState(ValidationState.FAILED)

    def _updateValidationState(self, validationState: ValidationState) -> None:
        if self.constraint is None:
            return

        if self.constraint.validationState != validationState:
            self.constraint.validationState = validationState
            self.validationStateUpdated.emit(self.constraint)


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

    focusedConstraintUpdated = Signal()
    focusedConstraintInputCountUpdated = Signal()
    focusedConstraintQualifiersUpdated = Signal()
    validateAllDone = Signal()

    def __init__(
        self,
        queryBuilder: QueryBuilder,
        sqlDatabase: SqlDatabase,
        wikibaseConfig: WikibaseConfig,
        wikibaseQueryRunner: WikibaseQueryRunner,
    ) -> None:
        super().__init__()

        self._queryBuilder = queryBuilder
        self._sqlDatabase = sqlDatabase
        self._wikibaseConfig = wikibaseConfig
        self._wikibaseQueryRunner = wikibaseQueryRunner

        self._constraintHelper = ConstraintHelper(
            self._queryBuilder,
            self._wikibaseConfig,
            self._wikibaseQueryRunner,
        )
        self._constraintHelper.inputCountUpdated.connect(self._onInputCountUpdated)
        self._constraintHelper.qualifiersUpdated.connect(self._onQualifiersUpdated)
        self._constraintHelper.violationsUpdated.connect(self._writeViolationsToSql)
        self._constraintHelper.validationStateUpdated.connect(
            self._updateValidationStateSql
        )
        self._constraintHelper.validationStateUpdated.connect(self._validateNextInQueue)

        self.constraints: Sequence[Constraint] = []
        self.focusedConstraint: Optional[Constraint] = None
        self._validationQueue: list[Constraint] = []
        self._validatingQueue = False

    def queryConstraints(self) -> None:
        query = self._queryBuilder.buildConstrainedPropertiesQuery()
        self._wikibaseQueryRunner.queueQueryForExecution(
            query, self._queryConstraintsResult
        )

    def _queryConstraintsResult(self) -> None:
        result = self._wikibaseQueryRunner.queryResult
        if not result:
            return
        self.constraints = []
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

                constraint.sqlRowId = len(self.constraints)
                self.constraints.append(constraint)
        except:
            return

        self._writeConstraintsListToSql()

    def _writeConstraintsListToSql(self) -> None:
        headerLabels = [column.value for column in ConstraintsTableColumn]

        table = [headerLabels] + [
            [
                c.sqlRowId,
                c.property.identifier,
                c.property.label,
                c.identifier,
                c.label,
                str(c.implemented),
                c.validationState.name,
            ]
            for c in self.constraints
        ]
        self._sqlDatabase.addTable("constraints", table)

    def setFocusedConstraint(self, rowId: int) -> None:
        if not (0 <= rowId < len(self.constraints)):
            return
        constraint = self.constraints[rowId]
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
            self._constraintHelper.queryExceptions(self.focusedConstraint)
            self._constraintHelper.queryViolations(self.focusedConstraint)

    def _updateValidationStateSql(self, c: Constraint) -> None:
        if c is None:
            raise RuntimeError(
                "validationStateUpdated signal should only be emitted when a corresponding constraint is set."
            )

        self._sqlDatabase.updateRow(
            "constraints",
            ("rowId", c.sqlRowId),
            {"validationState": c.validationState.name},
        )

    def validatingAll(self) -> bool:
        return len(self._validationQueue) != 0

    def stopValidatingAll(self) -> None:
        self._validationQueue = []
        self.validateAllDone.emit()

    def validateAll(self) -> None:
        self._validationQueue = list(self.constraints)
        self._validatingQueue = True
        self._validateNextInQueue()

    def _validateNextInQueue(self, c: Optional[Constraint] = None) -> None:
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
            self._constraintHelper.queryExceptions(constraint)
            self._constraintHelper.queryViolations(constraint)

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

    def _writeViolationsToSql(self, c: Constraint) -> None:
        if c.violations:
            table = [[i - 1] + list(row) for (i, row) in enumerate(c.violations)]
            table[0][0] = "rowId"

            self._sqlDatabase.addTable(c.tableName, table)

        if c.hiddenViolations:
            table = [[i - 1] + list(row) for (i, row) in enumerate(c.hiddenViolations)]
            table[0][0] = "rowId"

            self._sqlDatabase.addTable(c.tableName + "_hidden", table)
