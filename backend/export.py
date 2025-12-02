from collections import OrderedDict

import pandas as pd

from .wikibasehelper import BASE_URL
from .utils import urlFromId


def _addSheetData(writer, constraint, exportUrl):
    sheetName = f"{constraint.property.identifier}-{constraint.identifier}"
    sheetData = constraint.violations
    if exportUrl:
        sheetData = [
            [urlFromId(el, BASE_URL) if urlFromId(el, BASE_URL) else el for el in row]
            for row in sheetData
        ]
    pd.DataFrame(sheetData[1:]).to_excel(
        writer, sheet_name=sheetName, header=sheetData[0], index=False
    )


def exportSingleConstraintToOds(constraint, fileName, exportUrl):
    with pd.ExcelWriter(fileName) as writer:
        _addSheetData(writer, constraint, exportUrl)


def _addInfoSheetData(writer, constraints):
    sheetName = "Info"
    header = [
        "Prop ID",
        "Prop Label",
        "Constraint ID",
        "Constraint Label",
        "Violations",
    ]
    sheetData = [
        [
            c.property.identifier,
            c.property.label,
            c.identifier,
            c.label,
            len(c.violations) - 1,
        ]
        for c in constraints
    ]
    pd.DataFrame(sheetData).to_excel(
        writer, sheet_name=sheetName, header=header, index=False
    )


def exportMultipleConstraintsToOds(constraints, fileName, exportUrl):
    with pd.ExcelWriter(fileName) as writer:
        _addInfoSheetData(writer, constraints)
        for c in constraints:
            _addSheetData(writer, c, exportUrl)
