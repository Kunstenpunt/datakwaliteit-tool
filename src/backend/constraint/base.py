from enum import Enum
from functools import total_ordering

from typing import Optional, Self, Sequence
from ..wikibasehelper import WikibaseConfig


@total_ordering
class Item:
    def __init__(self, identifier: str, label: str) -> None:
        self.identifier = identifier
        self.label = label

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Item):
            return NotImplemented
        return (self.identifier, self.label) == (other.identifier, other.label)

    def __lt__(self, other: Self) -> bool:
        try:
            return int(self.identifier[1:]) < int(other.identifier[1:])
        except:
            return (self.identifier, self.label) < (
                other.identifier,
                other.label,
            )

    def __str__(self) -> str:
        if self.identifier == None and self.label == None:
            return "?"
        else:
            return f'"{self.label}" ({self.identifier})'


class Property(Item):
    def __init__(self, identifier: str, label: str) -> None:
        super().__init__(identifier, label)


class ValidationState(Enum):
    UNVALIDATED = 1
    VALIDATING = 2
    PARTIAL = 3
    VALIDATED = 4
    FAILED = 5


class ValidationMode(Enum):
    NO_LIMIT = 0
    LIMIT_OUTPUT = 1
    LIMIT_INPUT = 2


class ValidationInputCountType(Enum):
    STATEMENTS = 0
    ENTITIES = 1
    OTHER = 2


class Constraint(Item):
    def __init__(
        self,
        identifier: str,
        label: str,
        prop: Property,
        wikibaseConfig: WikibaseConfig,
    ) -> None:
        super().__init__(identifier, label)

        self.inputCount = -1
        self.validationState = ValidationState.UNVALIDATED

        self.doValidation = False
        self.implemented = False
        self.property = prop
        self.qualifiersObtained = False
        self.validationInputCountType = ValidationInputCountType.OTHER
        self.violations: Optional[Sequence[Sequence[str]]] = None
        self._wikibaseConfig = wikibaseConfig

        self.limit = 100000
        self.offset = 0
        self.sort = False
        self.validationMode = ValidationMode.NO_LIMIT

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Constraint):
            return NotImplemented
        return self.property == other.property and super().__eq__(other)

    def __lt__(self, other: Self) -> bool:
        return self.property < other.property or (
            (self.property == other.property) and super().__lt__(other)
        )

    def getPage(self) -> int:
        return int(self.offset / self.limit) + 1 if self.limit != 0 else 1

    def pretty(self) -> str:
        return f"{self}\non {self.property}"

    def getViolationsQuery(self) -> Optional[str]:
        print(f"Querying violations not implemented for {self}")
        return None

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        print(f"Updating qualifiers not implemented for {self}")

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        print(f"Updating violations not implemented for {self}")
