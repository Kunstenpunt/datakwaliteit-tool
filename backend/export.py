from collections import OrderedDict

import odswriter as ods
import xlsxwriter as xlsx

from .wikibasehelper import BASE_URL
from .utils import urlFromId


def _getSheetData(constraint, exportUrl):
    sheetName = f"{constraint.property.identifier}-{constraint.identifier}"
    sheetData = constraint.violations
    if exportUrl:
        sheetData = [
            [urlFromId(el, BASE_URL) if urlFromId(el, BASE_URL) else el for el in row]
            for row in sheetData
        ]
    return [sheetName, sheetData]


def _addSheetOds(odsFile, sheetName, sheetData):
    sheet = odsFile.new_sheet(sheetName)
    for row in sheetData:
        sheet.writerow(row)


def _addSheetXlsx(xlsxData, sheetName, sheetData):
    sheet = xlsxData.add_worksheet(sheetName)
    for i, row in enumerate(sheetData):
        sheet.write_row(i, 0, row)


def exportSingleConstraint(constraint, fileName, exportUrl):
    sheetName, sheetData = _getSheetData(constraint, exportUrl)
    if fileName.endswith(".ods"):
        with open(fileName, "wb") as f:
            with ods.writer(f) as odsFile:
                _addSheetOds(odsFile, sheetName, sheetData)
    if fileName.endswith(".xlsx"):
        xlsxData = xlsx.Workbook(fileName, {"constant_memory": True})
        _addSheetXlsx(xlsxData, sheetName, sheetData)
        xlsxData.close()


def _getInfoSheetData(constraints):
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
    return [sheetName, sheetData]


def exportMultipleConstraints(constraints, fileName, exportUrl):
    infoSheetName, infoSheetData = _getInfoSheetData(constraints)
    dataSheets = [_getSheetData(c, exportUrl) for c in constraints]
    if fileName.endswith(".ods"):
        with open(fileName, "wb") as f:
            with ods.writer(f) as odsFile:
                _addSheetOds(odsFile, infoSheetName, infoSheetData)
                for s in dataSheets:
                    _addSheetOds(odsFile, s[0], s[1])
    if fileName.endswith(".xlsx"):
        xlsxData = xlsx.Workbook(fileName, {"constant_memory": True})
        _addSheetXlsx(xlsxData, infoSheetName, infoSheetData)
        for s in dataSheets:
            _addSheetXlsx(xlsxData, s[0], s[1])
        xlsxData.close()
