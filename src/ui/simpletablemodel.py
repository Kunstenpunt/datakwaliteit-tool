from typing import Sequence

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
    QUrl,
)
from PySide6.QtGui import QBrush, QColor, QDesktopServices
from PySide6.QtWidgets import QHeaderView

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


class SimpleTableModel(QAbstractTableModel):
    def __init__(self, data: Sequence[Sequence[object]]) -> None:
        super().__init__()
        self._data: list[list[object]] = [list(inner) for inner in data]

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if role == Qt.ItemDataRole.DisplayRole:
            data = self._data[index.row() + 1][index.column()]
            if type(data) == type(True):
                return "✓" if data else "✗"
            if type(data) == ValidationState:
                return data.name
            return data

        if role == Qt.ItemDataRole.BackgroundRole:
            data = self._data[index.row() + 1][index.column()]
            if type(data) == type(True):
                return (
                    QBrush(Qt.GlobalColor.darkGreen)
                    if data
                    else QBrush(Qt.GlobalColor.darkRed)
                )
            if type(data) == ValidationState:
                match data:
                    case ValidationState.FAILED:
                        return QBrush(Qt.GlobalColor.darkRed)
                    case ValidationState.UNVALIDATED:
                        return QBrush(Qt.GlobalColor.darkGray)
                    case ValidationState.VALIDATED:
                        return QBrush(Qt.GlobalColor.darkGreen)
                    case ValidationState.PARTIAL:
                        return QBrush(QColor(0x60, 0x80, 0))
                    case ValidationState.VALIDATING:
                        return QBrush(Qt.GlobalColor.darkYellow)
        if role == Qt.ItemDataRole.ForegroundRole:
            data = self._data[index.row() + 1][index.column()]
            if type(data) == type(True) or type(data) == ValidationState:
                return QBrush(Qt.GlobalColor.white)

        return None

    def rowCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(self._data) - 1

    def columnCount(
        self, parent: QModelIndex | QPersistentModelIndex = QModelIndex()
    ) -> int:
        return len(self._data[0])

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> object:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._data[0][section]
        return None

    def setData(
        self,
        index: QModelIndex | QPersistentModelIndex,
        value: object,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> bool:
        self._data[index.row() + 1][index.column()] = value
        self.dataChanged.emit(index, index)
        return True
