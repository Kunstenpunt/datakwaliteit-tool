from typing import Sequence

import odswriter as ods
import xlsxwriter as xlsx

from PySide6.QtCore import QObject

from .constraints import Constraint, ValidationState
from .utils import urlFromId
from .wikibasehelper import WikibaseConfig


class Exporter(QObject):

    def __init__(self, wikibaseConfig: WikibaseConfig) -> None:
        super().__init__()

        self.wikibaseConfig = wikibaseConfig

    def _getSheetData(
        self, constraint: Constraint, exportUrl: bool
    ) -> tuple[str, Sequence[Sequence[str]]]:
        sheetName = f"{constraint.property.identifier}-{constraint.identifier}"
        sheetData = constraint.violations or []
        if exportUrl:
            sheetData = [
                [urlFromId(el, self.wikibaseConfig.getBaseUrl()) or el for el in row]
                for row in sheetData
            ]
        return (sheetName, sheetData)

    def _addSheetOds(
        self,
        odsFile: ods.ODSWriter,
        sheetName: str,
        sheetData: Sequence[Sequence[str | int]],
    ) -> None:
        sheet = odsFile.new_sheet(sheetName)  # type: ignore
        for row in sheetData:
            sheet.writerow(row)

    def _addSheetXlsx(
        self,
        xlsxData: xlsx.Workbook,
        sheetName: str,
        sheetData: Sequence[Sequence[str | int]],
    ) -> None:
        sheet = xlsxData.add_worksheet(sheetName)
        for i, row in enumerate(sheetData):
            sheet.write_row(i, 0, row)

    def exportSingleConstraint(
        self, constraint: Constraint, fileName: str, exportUrl: bool
    ) -> None:
        sheetName, sheetData = self._getSheetData(constraint, exportUrl)
        if fileName.endswith(".ods"):
            with open(fileName, "wb") as f:
                with ods.writer(f) as odsFile:  # type: ignore
                    self._addSheetOds(odsFile, sheetName, sheetData)
        if fileName.endswith(".xlsx"):
            xlsxData = xlsx.Workbook(fileName, {"constant_memory": True})
            self._addSheetXlsx(xlsxData, sheetName, sheetData)
            xlsxData.close()

    def _getInfoSheetData(
        self, constraints: Sequence[Constraint]
    ) -> tuple[str, Sequence[Sequence[str | int]]]:
        sheetName = "Info"
        sheetData: list[list[str | int]] = []
        sheetData.append(
            [
                "Prop ID",
                "Prop Label",
                "Constraint ID",
                "Constraint Label",
                "Violations",
                "Completeness",
            ]
        )
        sheetData += [
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
            if c.violations is not None
        ]
        return (sheetName, sheetData)

    def exportMultipleConstraints(
        self, constraints: Sequence[Constraint], fileName: str, exportUrl: bool
    ) -> None:
        infoSheetName, infoSheetData = self._getInfoSheetData(constraints)
        dataSheets = [self._getSheetData(c, exportUrl) for c in constraints]
        if fileName.endswith(".ods"):
            with open(fileName, "wb") as f:
                with ods.writer(f) as odsFile:  # type: ignore
                    self._addSheetOds(odsFile, infoSheetName, infoSheetData)
                    for s in dataSheets:
                        self._addSheetOds(odsFile, s[0], s[1])
        if fileName.endswith(".xlsx"):
            xlsxData = xlsx.Workbook(fileName, {"constant_memory": True})
            self._addSheetXlsx(xlsxData, infoSheetName, infoSheetData)
            for s in dataSheets:
                self._addSheetXlsx(xlsxData, s[0], s[1])
            xlsxData.close()
