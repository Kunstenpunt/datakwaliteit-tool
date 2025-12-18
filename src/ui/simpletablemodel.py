from PySide6.QtCore import (
    QAbstractTableModel,
    Qt,
    QUrl,
)
from PySide6.QtGui import QBrush, QColor, QDesktopServices
from PySide6.QtWidgets import QHeaderView

from ..backend.constraints import ValidationState
from ..backend.utils import urlFromId
from ..backend.wikibasehelper import BASE_URL


MAXIMUM_AUTO_TABLE_SECTION_WIDTH = 200


def onTableDoubleClicked(index):
    possibleID = index.data()
    url = urlFromId(possibleID, BASE_URL)
    if url:
        QDesktopServices.openUrl(QUrl(url))


def headerResizeNeatly(header):
    header.setMaximumSectionSize(MAXIMUM_AUTO_TABLE_SECTION_WIDTH)
    header.resizeSections(QHeaderView.ResizeMode.ResizeToContents)
    header.setMaximumSectionSize(-1)


class SimpleTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data

    def data(self, index, role):
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

    def rowCount(self, index):
        return len(self._data) - 1

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._data[0][section]

    def setData(self, index, value, role=None):
        self._data[index.row() + 1][index.column()] = value
        self.dataChanged.emit(index, index)
        return True
