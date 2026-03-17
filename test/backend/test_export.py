from itertools import product
import os

import ezodf
import pyexcel_xlsx
import pytest

from src.backend.constraint.base import Constraint, Property, ValidationState
from src.backend.export import Exporter
from test.backend.stubs import WikibaseConfigStub

constraintRecipes = {}
correctSheets = {}

constraintRecipes["validated_with_ids"] = {
    "constraintId": "Q1",
    "constraintLabel": "constraint 1",
    "propertyId": "P1",
    "propertyLabel": "property 1",
    "violations": [
        ["var1A", "var1B", "var1C"],
        ["Q11", "2", "P12"],
        ["Q12", "4", "P12"],
    ],
    "validationState": ValidationState.VALIDATED,
}

correctSheets["validated_with_ids_no_url"] = (
    "P1-Q1",
    [
        ["var1A", "var1B", "var1C"],
        ["Q11", "2", "P12"],
        ["Q12", "4", "P12"],
    ],
)

correctSheets["validated_with_ids_with_url"] = (
    "P1-Q1",
    [
        ["var1A", "var1B", "var1C"],
        ["https://base.url/entity/Q11", "2", "https://base.url/entity/P12"],
        ["https://base.url/entity/Q12", "4", "https://base.url/entity/P12"],
    ],
)

constraintRecipes["validated_no_ids"] = {
    "constraintId": "Q2",
    "constraintLabel": "constraint 2",
    "propertyId": "P1",
    "propertyLabel": "property 1",
    "violations": [["var2A", "var2B"]],
    "validationState": ValidationState.VALIDATED,
}

correctSheets["validated_no_ids"] = (
    "P1-Q2",
    [["var2A", "var2B"]],
)

constraintRecipes["unvalidated"] = {
    "constraintId": "Q2",
    "constraintLabel": "constraint 2",
    "propertyId": "P2",
    "propertyLabel": "property 2",
    "violations": None,
    "validationState": ValidationState.UNVALIDATED,
}

constraintRecipes["no_violations"] = {
    "constraintId": "Q3",
    "constraintLabel": "constraint 3",
    "propertyId": "P2",
    "propertyLabel": "property 2",
    "violations": [["var3A"]],
    "validationState": ValidationState.PARTIAL,
}

correctSheets["no_violations"] = (
    "P2-Q3",
    [["var3A"]],
)

correctSheets["info"] = (
    "Info",
    [
        [
            "Prop ID",
            "Prop Label",
            "Constraint ID",
            "Constraint Label",
            "Violations",
            "Completeness",
        ],
        ["P1", "property 1", "Q1", "constraint 1", 2, "complete"],
        ["P1", "property 1", "Q2", "constraint 2", 0, "complete"],
        ["P2", "property 2", "Q3", "constraint 3", 0, "partial"],
    ],
)


@pytest.fixture
def cleanupGeneratedFiles():
    yield
    for item in os.listdir():
        if item.endswith(".ods") or item.endswith(".xlsx"):
            os.remove(item)


def test_exportSingleConstraintValid(cleanupGeneratedFiles, subtests):
    constraintRecipeNames = [
        "validated_with_ids",
        "validated_no_ids",
        "no_violations",
    ]
    for fileExtension, exportUrl, constraintRecipeName in product(
        [".xlsx", ".ods"], [True, False], constraintRecipeNames
    ):
        with subtests.test(
            fileExtension=fileExtension,
            exportUrl=exportUrl,
            constraintRecipeName=constraintRecipeName,
        ):
            wikibaseConfigStub = WikibaseConfigStub()
            exporter = Exporter(wikibaseConfigStub)

            recipe = constraintRecipes[constraintRecipeName]
            constraint = buildConstraint(**recipe)

            filename = (
                "single_constraint_export_test_"
                + constraintRecipeName
                + ("_with_url" if exportUrl else "_no_url")
                + fileExtension
            )

            exporter.exportSingleConstraint(constraint, filename, exportUrl)

            correctBook = [getCorrectSheet(constraintRecipeName, exportUrl)]

            checkFileContents(filename, correctBook)


def test_exportMultipleConstraintOds(cleanupGeneratedFiles, subtests):
    for fileExtension, exportUrl in product([".xlsx", ".ods"], [True, False]):
        with subtests.test(fileExtension=fileExtension, exportUrl=exportUrl):
            wikibaseConfigStub = WikibaseConfigStub()
            exporter = Exporter(wikibaseConfigStub)

            constraints = [
                buildConstraint(**constraintRecipes[recipe])
                for recipe in [
                    "validated_with_ids",
                    "validated_no_ids",
                    "unvalidated",
                    "no_violations",
                ]
            ]

            filename = (
                "multiple_constraints_export_test_"
                + ("with_url" if exportUrl else "no_url")
                + fileExtension
            )

            exporter.exportMultipleConstraints(constraints, filename, exportUrl)

            correctBook = [
                getCorrectSheet("info", exportUrl),
                getCorrectSheet("validated_with_ids", exportUrl),
                getCorrectSheet("validated_no_ids", exportUrl),
                getCorrectSheet("no_violations", exportUrl),
            ]

            checkFileContents(filename, correctBook)


def buildConstraint(
    constraintId,
    constraintLabel,
    propertyId,
    propertyLabel,
    violations,
    validationState,
):
    property = Property(propertyId, propertyLabel)
    constraint = Constraint(constraintId, constraintLabel, property)
    constraint.violations = violations
    constraint.validationState = validationState
    return constraint


def getCorrectSheet(constraintRecipeName, exportUrl=False):
    correctSheetKey = constraintRecipeName
    if constraintRecipeName == "validated_with_ids":
        correctSheetKey += "_with_url" if exportUrl else "_no_url"
    return correctSheets[correctSheetKey]


def checkFileContents(filename, correctBook):
    assert os.path.exists(filename)
    currentBook = readBook(filename)
    assert currentBook == correctBook


def readBook(filename):
    if filename.endswith(".xlsx"):
        return list(pyexcel_xlsx.get_data(filename).items())
    elif filename.endswith(".ods"):
        book = []
        for odsSheet in ezodf.opendoc(filename).sheets:
            sheetName = odsSheet.name
            sheetData = [[cell.value for cell in row] for row in odsSheet.rows()]
            book.append((sheetName, sheetData))
        return book
