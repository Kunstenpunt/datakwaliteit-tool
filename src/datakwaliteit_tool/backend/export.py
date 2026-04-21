from typing import Sequence

import odswriter as ods
import xlsxwriter as xlsx

from PySide6.QtCore import QObject

from .constraint.base import Constraint, ValidationState
from .types import T, Table
from .utils import urlFromId
from .wikibasehelper import WikibaseConfig

SheetName = str
Sheet = tuple[SheetName, Table[T]]


class Exporter(QObject):

    def __init__(self, wikibaseConfig: WikibaseConfig) -> None:
        super().__init__()

        self.wikibaseConfig = wikibaseConfig

    def exportSingleConstraint(
        self, constraint: Constraint, fileName: str, exportUrl: bool
    ) -> None:
        sheets = [self._getSheetData(constraint, exportUrl)]
        self._writeSheetsToFile(sheets, fileName)

    def exportMultipleConstraints(
        self, constraints: Sequence[Constraint], fileName: str, exportUrl: bool
    ) -> None:
        sheets = [self._getInfoSheetData(constraints)] + [
            self._getSheetData(c, exportUrl)
            for c in constraints
            if c.violations is not None
        ]
        self._writeSheetsToFile(sheets, fileName)

    def _getSheetData(self, constraint: Constraint, exportUrl: bool) -> Sheet[str]:
        sheetName = f"{constraint.property.identifier}-{constraint.identifier}"
        sheetData = constraint.violations or []
        if exportUrl:
            sheetData = [
                [urlFromId(el, self.wikibaseConfig.baseUrl) or el for el in row]
                for row in sheetData
            ]
        return (sheetName, sheetData)

    def _getInfoSheetData(self, constraints: Sequence[Constraint]) -> Sheet[str | int]:
        sheetName = "Info"
        sheetData: Table[str | int] = [
            [
                "Prop ID",
                "Prop Label",
                "Constraint ID",
                "Constraint Label",
                "Violations",
                "Completeness",
            ]
        ] + [
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

    def _writeSheetsToFile(
        self, sheets: Sequence[Sheet[str | int]], fileName: str
    ) -> None:
        if fileName.endswith(".ods"):
            with open(fileName, "wb") as f:
                with ods.writer(f) as odsFile:  # type: ignore
                    for s in sheets:
                        self._addSheetOds(odsFile, s)
        if fileName.endswith(".xlsx"):
            xlsxData = xlsx.Workbook(fileName, {"constant_memory": True})
            for s in sheets:
                self._addSheetXlsx(xlsxData, s)
            xlsxData.close()

    def _addSheetOds(
        self,
        odsFile: ods.ODSWriter,
        sheet: Sheet[str | int],
    ) -> None:
        sheetName, sheetData = sheet
        odsSheet = odsFile.new_sheet(sheetName)  # type: ignore
        for row in sheetData:
            odsSheet.writerow(row)

    def _addSheetXlsx(
        self,
        xlsxData: xlsx.Workbook,
        sheet: Sheet[str | int],
    ) -> None:
        sheetName, sheetData = sheet
        xlsxSheet = xlsxData.add_worksheet(sheetName)
        for i, row in enumerate(sheetData):
            xlsxSheet.write_row(i, 0, row)
