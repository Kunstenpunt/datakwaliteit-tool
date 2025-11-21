from collections import OrderedDict

from pyexcel_ods3 import save_data as saveData

from .wikibasehelper import BASE_URL
from .utils import urlFromId


def _createSheetData(constraint, exportUrl):
    sheetName = f"{constraint.property.identifier}-{constraint.identifier}"
    sheetData = constraint.violations
    if exportUrl:
        sheetData = [
            [urlFromId(el, BASE_URL) if urlFromId(el, BASE_URL) else el for el in row]
            for row in sheetData
        ]
    return {sheetName: sheetData}


def exportSingleConstraintToOds(constraint, fileName, exportUrl):
    data = OrderedDict()
    data.update(_createSheetData(constraint, exportUrl))
    saveData(fileName, data)


def _createInfoSheetData(constraints, exportUrl):
    sheetName = "Info"
    header = [
        "Prop ID",
        "Prop Label",
        "Constraint ID",
        "Constraint Label",
        "Violations",
    ]
    sheetData = [header] + [
        [
            c.property.identifier,
            c.property.label,
            c.identifier,
            c.label,
            len(c.violations) - 1,
        ]
        for c in constraints
    ]
    return {sheetName: sheetData}


def exportMultipleConstraintsToOds(constraints, fileName, exportUrl):
    data = OrderedDict()
    data.update(_createInfoSheetData(constraints, exportUrl))
    for c in constraints:
        data.update(_createSheetData(c, exportUrl))
    saveData(fileName, data)
