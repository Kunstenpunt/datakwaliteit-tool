import odswriter as ods
import xlsxwriter as xlsx

from PySide6.QtCore import QObject

from .constraints import ValidationState
from .utils import urlFromId


class Exporter(QObject):

    def __init__(self, wikibaseHelper):
        super().__init__()

        self.wikibaseHelper = wikibaseHelper

    def _getSheetData(self, constraint, exportUrl):
        sheetName = f"{constraint.property.identifier}-{constraint.identifier}"
        sheetData = constraint.violations
        if exportUrl:
            sheetData = [
                [
                    (
                        urlFromId(el, self.wikibaseHelper.getBaseUrl())
                        if urlFromId(el, self.wikibaseHelper.getBaseUrl())
                        else el
                    )
                    for el in row
                ]
                for row in sheetData
            ]
        return [sheetName, sheetData]

    def _addSheetOds(self, odsFile, sheetName, sheetData):
        sheet = odsFile.new_sheet(sheetName)
        for row in sheetData:
            sheet.writerow(row)

    def _addSheetXlsx(self, xlsxData, sheetName, sheetData):
        sheet = xlsxData.add_worksheet(sheetName)
        for i, row in enumerate(sheetData):
            sheet.write_row(i, 0, row)

    def exportSingleConstraint(self, constraint, fileName, exportUrl):
        sheetName, sheetData = self._getSheetData(constraint, exportUrl)
        if fileName.endswith(".ods"):
            with open(fileName, "wb") as f:
                with ods.writer(f) as odsFile:
                    self._addSheetOds(odsFile, sheetName, sheetData)
        if fileName.endswith(".xlsx"):
            xlsxData = xlsx.Workbook(fileName, {"constant_memory": True})
            self._addSheetXlsx(xlsxData, sheetName, sheetData)
            xlsxData.close()

    def _getInfoSheetData(self, constraints):
        sheetName = "Info"
        header = [
            "Prop ID",
            "Prop Label",
            "Constraint ID",
            "Constraint Label",
            "Violations",
            "Completeness",
        ]
        sheetData = [header] + [
            [
                c.property.identifier,
                c.property.label,
                c.identifier,
                c.label,
                len(c.violations) - 1,
                (
                    "partial"
                    if c.validationState == ValidationState.PARTIAL
                    else "complete"
                ),
            ]
            for c in constraints
        ]
        return [sheetName, sheetData]

    def exportMultipleConstraints(self, constraints, fileName, exportUrl):
        infoSheetName, infoSheetData = self._getInfoSheetData(constraints)
        dataSheets = [self._getSheetData(c, exportUrl) for c in constraints]
        if fileName.endswith(".ods"):
            with open(fileName, "wb") as f:
                with ods.writer(f) as odsFile:
                    self._addSheetOds(odsFile, infoSheetName, infoSheetData)
                    for s in dataSheets:
                        self._addSheetOds(odsFile, s[0], s[1])
        if fileName.endswith(".xlsx"):
            xlsxData = xlsx.Workbook(fileName, {"constant_memory": True})
            self._addSheetXlsx(xlsxData, infoSheetName, infoSheetData)
            for s in dataSheets:
                self._addSheetXlsx(xlsxData, s[0], s[1])
            xlsxData.close()
