from enum import auto, Enum
from typing import Optional, Sequence


from .base import (
    Constraint,
    Item,
    Property,
    ValidationInputCountType,
)

from ..utils import idFromUrl


class RelationType(Enum):
    INSTANCE_OF = auto()
    SUBCLASS_OF = auto()
    INSTANCE_OR_SUBCLASS_OF = auto()
    UNKNOWN = auto()


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Single_value
class SingleValueConstraint(Constraint):

    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.separators: Sequence[Property] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.separators:
            label += f"\nseparator(s): {[str(s) for s in self.separators]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.separators = [
                Property(idFromUrl(identifier), label)
                for [identifier, label] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(i), iL, v] for [s, i, iL, v] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Value_class
class ValueTypeConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.classes: Sequence[Item] = []
        self.relation = RelationType.UNKNOWN

    def pretty(self) -> str:
        label = super().pretty()
        if self.classes:
            label += f"\nclass(es): {[str(s) for s in self.classes]}, relation: {self.relation.name}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        classes = []

        try:
            for [classId, classLabel, relationId, relationLabel] in result[1:]:
                classId = idFromUrl(classId)
                classes.append(Item(classId, classLabel))

                if self.relation == RelationType.UNKNOWN:
                    match relationLabel:
                        case "instance of":
                            self.relation = RelationType.INSTANCE_OF
                        case "subclass of":
                            self.relation = RelationType.SUBCLASS_OF
                        case "instance or subclass of":
                            self.relation = RelationType.INSTANCE_OR_SUBCLASS_OF
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.classes = classes
        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(i), iL, idFromUrl(v), vL]
                for [s, i, iL, v, vL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Subject_class
class SubjectTypeConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.ENTITIES

        self.classes: Sequence[Item] = []
        self.relation = RelationType.UNKNOWN

    def pretty(self) -> str:
        label = super().pretty()
        if self.classes is not None and len(self.classes):
            label += f"\nclass(es): {[str(s) for s in self.classes]}, relation: {self.relation.name}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        classes = []
        try:
            for [classId, classLabel, relationId, relationLabel] in result[1:]:
                classId = idFromUrl(classId)
                classes.append(Item(classId, classLabel))

                if self.relation == RelationType.UNKNOWN:
                    match relationLabel:
                        case "instance of":
                            self.relation = RelationType.INSTANCE_OF
                        case "subclass of":
                            self.relation = RelationType.SUBCLASS_OF
                        case "instance or subclass of":
                            self.relation = RelationType.INSTANCE_OR_SUBCLASS_OF
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.classes = classes
        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(i), iL] for [s, i, iL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Required_qualifiers
class RequiredQualifierConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.requiredQualifiers: Sequence[Property] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.requiredQualifiers:
            label += (
                f"\nrequired qualifiers: {[str(q) for q in self.requiredQualifiers]}"
            )
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.requiredQualifiers = [
                Property(idFromUrl(propId), propLabel)
                for [propId, propLabel] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(i), iL] for [s, i, iL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Qualifiers
class AllowedQualifiersConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.allowedQualifiers: Sequence[Property] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.allowedQualifiers:
            label += f"\nallowed qualifiers: {[str(q) for q in self.allowedQualifiers]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.allowedQualifiers = [
                Property(idFromUrl(propId), propLabel)
                for [propId, propLabel] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(i), iL] for [s, i, iL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Conflicts_with
class ConflictsWithConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.ENTITIES
        self.conflictingStatements: Sequence[tuple[Property, Optional[Item]]] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.conflictingStatements:
            label += f"\nconflicting statements: {[f"{str(p)}{" " + str(v) if v else ""}" for (p,v) in self.conflictingStatements]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.conflictingStatements = [
                (
                    Property(idFromUrl(propId), propLabel),
                    Item(valueId, valueLabel) if valueId else None,
                )
                for [propId, propLabel, valueId, valueLabel] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(i), iL] for [s, i, iL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Unique_value
class DistinctValuesConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.separators: Sequence[Property] = []

    def pretty(self) -> str:
        label = super().pretty()
        if self.separators:
            label += f"\nseparator(s): {[str(s) for s in self.separators]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.separators = [
                Property(idFromUrl(identifier), label)
                for [identifier, label] in result[1:]
            ]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        if self.separators:
            print(
                "Warning: validation hasn't been tested yet with separators, could explode violently."
            )
        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(i), iL, idFromUrl(v), vL]
                for [s, i, iL, v, vL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Format
class FormatConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS

        self.format = ""

    def pretty(self) -> str:
        label = super().pretty()
        if self.format:
            label += f"\nformat: {self.format}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.format = result[1][0]
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [
                    idFromUrl(s),
                    idFromUrl(i),
                    iL,
                    v,
                ]
                for [s, i, iL, v] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Item
class ItemRequiresStatementConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.ENTITIES
        self.requiredStatements: dict[str, tuple[Property, list[Item]]] = {}

    def pretty(self) -> str:
        label = super().pretty()
        if self.requiredStatements:
            label += f"\nrequiredStatement: {[f"{str(s[0])} = " + ", ".join(str(v) for v in s[1]) for s in self.requiredStatements.values()]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        self.requiredStatements = {}
        try:
            for [propId, propLabel, valueId, valueLabel] in result[1:]:
                prop = Property(idFromUrl(propId), propLabel)
                if not (prop.identifier in self.requiredStatements):
                    self.requiredStatements[prop.identifier] = (prop, [])
                if valueId != None:
                    value = Item(idFromUrl(valueId), valueLabel)
                    self.requiredStatements[prop.identifier][1].append(value)
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(i), iL] for [s, i, iL] in result
            ]
        except:
            return


# https://www.wikidata.org/wiki/Help:Property_constraints_portal/Target_required_claim
class ValueRequiresStatementConstraint(Constraint):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
    ) -> None:
        super().__init__(identifier, label, prop)
        self.implemented = True
        self.validationInputCountType = ValidationInputCountType.STATEMENTS
        self.requiredStatements: dict[str, tuple[Property, list[Item]]] = {}

    def pretty(self) -> str:
        label = super().pretty()
        if self.requiredStatements:
            label += f"\nrequiredStatement: {[f"{str(s[0])} = " + ", ".join(str(v) for v in s[1]) for s in self.requiredStatements.values()]}"
        return label

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        self.requiredStatements = {}
        try:
            for [propId, propLabel, valueId, valueLabel] in result[1:]:
                prop = Property(idFromUrl(propId), propLabel)
                if not (prop.identifier in self.requiredStatements):
                    self.requiredStatements[prop.identifier] = (prop, [])
                if valueId != None:
                    value = Item(idFromUrl(valueId), valueLabel)
                    self.requiredStatements[prop.identifier][1].append(value)
        except:
            raise ValueError("{result} is an invalid value for updating qualifiers")

        self.qualifiersObtained = True

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        try:
            self.violations = [
                [idFromUrl(s), idFromUrl(i), iL, idFromUrl(v), vL]
                for [s, i, iL, v, vL] in result
            ]
        except:
            return
