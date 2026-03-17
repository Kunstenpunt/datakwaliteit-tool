from enum import Enum
from functools import total_ordering

from typing import Optional, Self, Sequence
from ..wikibasehelper import WikibaseConfig


@total_ordering
class Entity:
    def __init__(self, identifier: str, label: str) -> None:
        self._prefix = ""
        self.number = 0

        self.identifier = identifier
        self.label = label

    @property
    def prefix(self) -> str:
        return self._prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        if value not in ("Q", "P", "L"):
            raise ValueError(f"{value} is an invalid value for entity prefix")
        self._prefix = value

    @property
    def identifier(self) -> str:
        return f"{self.prefix}{self.number}"

    @identifier.setter
    def identifier(self, value: str) -> None:
        try:
            self.prefix = value[0]
            self.number = int(value[1:])
        except:
            raise ValueError(f"{value} is an invalid value for entity identifier")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return (self.prefix, self.number, self.label) == (
            other.prefix,
            other.number,
            other.label,
        )

    def __lt__(self, other: Self) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return (self.prefix, self.number, self.label) < (
            other.prefix,
            other.number,
            other.label,
        )

    def __str__(self) -> str:
        return f'"{self.label}" ({self.identifier})'


class Item(Entity):
    def __init__(self, identifier: str, label: str) -> None:
        super().__init__(identifier, label)

    @property
    def prefix(self) -> str:
        return super().prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        if value != "Q":
            raise ValueError(f"{value} is an invalid value for item prefix")
        self._prefix = value


class Property(Entity):
    def __init__(self, identifier: str, label: str) -> None:
        super().__init__(identifier, label)

    @property
    def prefix(self) -> str:
        return super().prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        if value != "P":
            raise ValueError(f"{value} is an invalid value for property prefix")
        self._prefix = value


class Lexeme(Entity):
    def __init__(self, identifier: str, label: str) -> None:
        super().__init__(identifier, label)

    @property
    def prefix(self) -> str:
        return super().prefix

    @prefix.setter
    def prefix(self, value: str) -> None:
        if value != "L":
            raise ValueError(f"{value} is an invalid value for lexeme prefix")
        self._prefix = value


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
    ) -> None:
        super().__init__(identifier, label)

        self.property = prop

        self.inputCount = -1
        self.validationInputCountType = ValidationInputCountType.OTHER

        self.exceptionIds: Optional[Sequence[str]] = None

        self.doValidation = False
        self.implemented = False
        self.qualifiersObtained = False
        self.validationState = ValidationState.UNVALIDATED
        self.violations: Optional[Sequence[Sequence[str]]] = None

        self.limit = 100000
        self._offset = 0
        self.sort = False
        self.validationMode = ValidationMode.NO_LIMIT

    @property
    def page(self) -> int:
        return int(self._offset / self.limit) + 1 if self.limit != 0 else 1

    @page.setter
    def page(self, value: int) -> None:
        if value <= 0:
            raise ValueError(f"{value} is an invalid value for constraint page")
        self._offset = (value - 1) * self.limit

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Constraint):
            return NotImplemented
        return self.property == other.property and super().__eq__(other)

    def __lt__(self, other: Self) -> bool:
        return self.property < other.property or (
            (self.property == other.property) and super().__lt__(other)
        )

    def pretty(self) -> str:
        return f"{self}\non {self.property}"

    def getViolationsQuery(self) -> Optional[str]:
        print(f"Querying violations not implemented for {self}")
        return None

    def updateQualifiers(self, result: Sequence[Sequence[str]]) -> None:
        print(f"Updating qualifiers not implemented for {self}")

    def updateViolations(self, result: Sequence[Sequence[str]]) -> None:
        print(f"Updating violations not implemented for {self}")
