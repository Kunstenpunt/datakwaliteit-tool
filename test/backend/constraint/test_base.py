import pytest

from src.datakwaliteit_tool.backend.constraint.base import (
    Constraint,
    Entity,
    Item,
    Property,
    Lexeme,
    ValidationInputCountType,
    ValidationMode,
    ValidationState,
)

from test.backend.stubs import WikibaseConfigStub


def test_Entity__init__():
    item = Entity("Q1", "item1")
    assert item.identifier == "Q1"
    assert item.prefix == "Q"
    assert item.number == 1
    assert item.label == "item1"
    prop = Entity("P2", "prop1")
    assert prop.identifier == "P2"
    assert prop.prefix == "P"
    assert prop.number == 2
    assert prop.label == "prop1"
    lexeme = Entity("L3", "lexeme1")
    assert lexeme.identifier == "L3"
    assert lexeme.prefix == "L"
    assert lexeme.number == 3
    assert lexeme.label == "lexeme1"
    entityNoLabel = Entity("Q1", "")
    assert entityNoLabel.identifier == "Q1"
    assert entityNoLabel.prefix == "Q"
    assert entityNoLabel.number == 1
    assert entityNoLabel.label == ""

    with pytest.raises(ValueError):
        Entity("R1", "item1")
    with pytest.raises(ValueError):
        Entity("Q1!", "item1")
    with pytest.raises(ValueError):
        Entity("Q", "item1")


def test_EntityProps():
    entity = Entity("Q1", "item")
    entity.prefix = "P"
    entity.number = 2
    entity.label = "prop"
    assert entity.prefix == "P"
    assert entity.number == 2
    assert entity.identifier == "P2"
    assert entity.label == "prop"
    entity.identifier = "L3"
    assert entity.prefix == "L"
    assert entity.number == 3
    assert entity.identifier == "L3"
    assert entity.label == "prop"

    with pytest.raises(ValueError):
        entity.prefix = "3"
    with pytest.raises(ValueError):
        entity.prefix = "T"
    with pytest.raises(ValueError):
        entity.identifier = "P1!"
    with pytest.raises(ValueError):
        entity.identifier = "P"
    with pytest.raises(ValueError):
        entity.identifier = "S1"


def test_Entity__eq__():
    assert Entity("Q1", "item") == Entity("Q1", "item")
    assert Entity("Q1", "item") != Entity("Q2", "item")
    assert Entity("Q1", "item") != Entity("P1", "item")
    assert Entity("Q1", "item") != Entity("Q1", "other")
    assert Entity("Q1", "item") != 5
    assert Entity("Q1", "item").__eq__(5) == NotImplemented


def test_Entity__lt__():
    assert Entity("Q1", "item") < Entity("Q2", "item")
    assert Entity("Q11", "item") > Entity("Q2", "item")
    assert Entity("Q1", "a") < Entity("Q1", "b")
    assert Entity("Q2", "a") > Entity("Q1", "b")
    with pytest.raises(TypeError):
        Entity("Q1", "item") < 2
    assert Entity("Q1", "item").__lt__(2) == NotImplemented


def test_Entity__str__():
    assert str(Entity("Q1", "item1")) == '"item1" (Q1)'
    assert str(Entity("Q1", "")) == '"" (Q1)'


def test_Item():
    item = Item("Q1", "item1")
    assert item.prefix == "Q"
    assert item.number == 1
    assert item.identifier == "Q1"
    assert item.label == "item1"

    with pytest.raises(ValueError):
        item.prefix = "P"
    with pytest.raises(ValueError):
        item.prefix = "L"
    with pytest.raises(ValueError):
        item.identifier = "P1"

    with pytest.raises(ValueError):
        Item("P1", "item1")
    with pytest.raises(ValueError):
        Item("Q1!", "item1")
    with pytest.raises(ValueError):
        Item("Q", "item1")


def test_Property():
    prop = Property("P1", "prop1")
    assert prop.prefix == "P"
    assert prop.number == 1
    assert prop.identifier == "P1"
    assert prop.label == "prop1"

    with pytest.raises(ValueError):
        prop.prefix = "Q"
    with pytest.raises(ValueError):
        prop.prefix = "L"
    with pytest.raises(ValueError):
        prop.identifier = "L1"

    with pytest.raises(ValueError):
        Property("Q1", "prop1")
    with pytest.raises(ValueError):
        Property("P1!", "prop1")
    with pytest.raises(ValueError):
        Property("P", "prop1")


def test_Lexeme():
    lexeme = Lexeme("L1", "lexeme1")
    assert lexeme.prefix == "L"
    assert lexeme.number == 1
    assert lexeme.identifier == "L1"
    assert lexeme.label == "lexeme1"

    with pytest.raises(ValueError):
        lexeme.prefix = "Q"
    with pytest.raises(ValueError):
        lexeme.prefix = "P"
    with pytest.raises(ValueError):
        lexeme.identifier = "P1"

    with pytest.raises(ValueError):
        Lexeme("P1", "lexeme1")
    with pytest.raises(ValueError):
        Lexeme("L1!", "lexeme1")
    with pytest.raises(ValueError):
        Lexeme("L", "lexeme1")


def test_Constraint():
    constraint = Constraint("Q1", "constraint1", Property("P1", "prop1"))
    assert constraint.property == Property("P1", "prop1")

    assert constraint.violations == None
    assert constraint.hiddenViolations == None
    assert constraint.exceptionIds == None

    assert constraint.inputCount == -1
    assert constraint.validationInputCountType == ValidationInputCountType.OTHER

    assert constraint.doValidation == False
    assert constraint.implemented == False
    assert constraint.qualifiersObtained == False
    assert constraint.validationState == ValidationState.UNVALIDATED

    assert constraint._offset == 0
    assert constraint.sort == False
    assert constraint.validationMode == ValidationMode.NO_LIMIT

    assert constraint.page == 1

    constraint.limit = 10
    constraint.page = 5
    assert constraint._offset == 40
    assert constraint.page == 5

    with pytest.raises(ValueError):
        constraint.page = 0
    with pytest.raises(ValueError):
        constraint.page = -1


def test_ConstraintViolationsThenExceptions():
    constraint = Constraint("Q1", "constraint1", Property("P1", "prop1"))

    constraint.violations = [
        ["statement", "item"],
        ["X1", "Q4"],
        ["X2", "Q3"],
        ["X3", "Q1"],
        ["X4", "Q6"],
    ]
    assert constraint.violations == [
        ["statement", "item"],
        ["X1", "Q4"],
        ["X2", "Q3"],
        ["X3", "Q1"],
        ["X4", "Q6"],
    ]
    assert constraint.hiddenViolations == None
    assert constraint.exceptionIds == None

    constraint.exceptionIds = ["Q1", "Q5", "Q4"]
    assert constraint.violations == [["statement", "item"], ["X2", "Q3"], ["X4", "Q6"]]
    assert constraint.hiddenViolations == [
        ["statement", "item"],
        ["X1", "Q4"],
        ["X3", "Q1"],
    ]
    assert constraint.exceptionIds == ["Q1", "Q5", "Q4"]


def test_ConstraintExceptionsThenViolations():
    constraint = Constraint("Q1", "constraint1", Property("P1", "prop1"))

    constraint.exceptionIds = ["Q1", "Q5", "Q4"]
    assert constraint.violations == None
    assert constraint.hiddenViolations == None
    assert constraint.exceptionIds == ["Q1", "Q5", "Q4"]

    constraint.violations = [
        ["statement", "item"],
        ["X1", "Q4"],
        ["X2", "Q3"],
        ["X3", "Q1"],
        ["X4", "Q6"],
    ]
    assert constraint.violations == [["statement", "item"], ["X2", "Q3"], ["X4", "Q6"]]
    assert constraint.hiddenViolations == [
        ["statement", "item"],
        ["X1", "Q4"],
        ["X3", "Q1"],
    ]
    assert constraint.exceptionIds == ["Q1", "Q5", "Q4"]


def test_ConstraintPretty():
    constraint = Constraint("Q1", "constraint1", Property("P1", "prop1"))

    assert constraint.pretty() == '"constraint1" (Q1)\non "prop1" (P1)'
