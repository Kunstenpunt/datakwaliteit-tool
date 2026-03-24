from typing import Optional

from PySide6.QtCore import QSortFilterProxyModel

from PySide6.QtWidgets import QTableView, QWidget

from ..backend.constraint.base import Constraint
from .simpletablemodel import headerResizeNeatly, SimpleTableModel


class ViolationsTable(QTableView):
    def __init__(self, parent: Optional[QWidget]) -> None:
        super().__init__(parent)
        self.violationsItemModel = QSortFilterProxyModel()

    def updateViolations(self, constraint: Constraint) -> None:
        if constraint.violations is None:
            self.setModel(None)
            return
        self.violationsItemModel.setSourceModel(SimpleTableModel(constraint.violations))
        self.setModel(self.violationsItemModel)
        header = self.horizontalHeader()
        headerResizeNeatly(header)
        header.resizeSection(0, header.defaultSectionSize())
