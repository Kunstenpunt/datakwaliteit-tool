from typing import Optional, Sequence

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    QItemSelection,
    QItemSelectionModel,
    Qt,
    QUrl,
)
from PySide6.QtGui import QBrush, QColor, QDesktopServices
from PySide6.QtWidgets import QHeaderView
from PySide6.QtSql import QSqlTableModel

from ..backend.constraint.base import ValidationState
from ..backend.utils import urlFromId
from ..backend.wikibasehelper import WikibaseConfig

MAXIMUM_AUTO_TABLE_SECTION_WIDTH = 200


class TableClickHandler:
    def __init__(self, wikibaseConfig: WikibaseConfig) -> None:
        super().__init__()
        self._wikibaseConfig = wikibaseConfig

    def onTableDoubleClicked(self, index: QModelIndex) -> None:
        possibleID = index.data()
        url = urlFromId(possibleID, self._wikibaseConfig.getBaseUrl())
        if url:
            QDesktopServices.openUrl(QUrl(url))


def headerResizeNeatly(header: QHeaderView) -> None:
    header.setMaximumSectionSize(MAXIMUM_AUTO_TABLE_SECTION_WIDTH)
    header.resizeSections(QHeaderView.ResizeMode.ResizeToContents)
    header.setMaximumSectionSize(-1)


class SqlTableModel(QSqlTableModel):
    def __init__(self) -> None:
        super().__init__()

        self.selectionModel: Optional[QItemSelectionModel] = None

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        data = QSqlTableModel.data(self, index, Qt.ItemDataRole.DisplayRole)
        if role == Qt.ItemDataRole.DisplayRole:
            match data:
                case "True":
                    return "✓"
                case "False":
                    return "✗"
                case other:
                    return other

        if role == Qt.ItemDataRole.BackgroundRole:
            match data:
                case "True":
                    return QBrush(Qt.GlobalColor.darkGreen)
                case "False":
                    return QBrush(Qt.GlobalColor.darkRed)
                case ValidationState.FAILED.name:
                    return QBrush(Qt.GlobalColor.darkRed)
                case ValidationState.UNVALIDATED.name:
                    return QBrush(Qt.GlobalColor.darkGray)
                case ValidationState.VALIDATED.name:
                    return QBrush(Qt.GlobalColor.darkGreen)
                case ValidationState.PARTIAL.name:
                    return QBrush(QColor(0x60, 0x80, 0))
                case ValidationState.VALIDATING.name:
                    return QBrush(Qt.GlobalColor.darkYellow)
        if role == Qt.ItemDataRole.ForegroundRole:
            if data in [
                "True",
                "False",
                ValidationState.FAILED.name,
                ValidationState.UNVALIDATED.name,
                ValidationState.VALIDATED.name,
                ValidationState.PARTIAL.name,
                ValidationState.VALIDATING.name,
            ]:
                return QBrush(Qt.GlobalColor.white)

        return None

    def select(self) -> bool:
        selectedRowId = self._getSelectedRowId()

        if not QSqlTableModel.select(self):
            return False

        self._fetchAll()

        self._selectRowId(selectedRowId)

        return True

    def _getSelectedRowId(self) -> int:
        if self.selectionModel:
            selectedIndexes = self.selectionModel.selectedIndexes()
            if selectedIndexes:
                currentRow = selectedIndexes[0].row()
                return int(self.index(currentRow, 0).data(Qt.ItemDataRole.DisplayRole))

        return -1

    def _selectRowId(self, rowId: int) -> None:
        if rowId == -1 or not self.selectionModel:
            return

        start = self.index(0, 0)
        foundIndexes = self.match(
            start, Qt.ItemDataRole.DisplayRole, rowId, flags=Qt.MatchFlag.MatchExactly
        )
        if foundIndexes:
            selection = QItemSelection(
                foundIndexes[0],
                foundIndexes[0].siblingAtColumn(self.columnCount() - 1),
            )
            self.selectionModel.select(
                selection, QItemSelectionModel.SelectionFlag.Select
            )

    def _fetchAll(self) -> None:
        while self.canFetchMore():
            self.fetchMore()
