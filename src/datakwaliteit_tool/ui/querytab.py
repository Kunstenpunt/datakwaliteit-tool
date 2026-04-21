from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtWidgets import QWidget

from ..backend.model import Model
from ..backend.utils import stripUrlPartFromTable

from .designer.querytab import Ui_QueryTab
from .simpletablemodel import (
    headerResizeNeatly,
    SqlTableModel,
    TableClickHandler,
)


class QueryTab(QWidget, Ui_QueryTab):
    def __init__(self, model: Model) -> None:
        super().__init__()
        self.setupUi(self)  # type: ignore

        self.model = model

        self.copyButton.clicked.connect(self.copy)
        self.executeButton.clicked.connect(self.onExecuteButtonClicked)
        self.tableClickHandler = TableClickHandler(self.model.wikibaseConfig)
        self.tableView.doubleClicked.connect(
            self.tableClickHandler.onTableDoubleClicked
        )
        self.tableModel = SqlTableModel()
        self.tableView.setModel(self.tableModel)
        self.tableModel.selectionModel = self.tableView.selectionModel()

    def copy(self) -> None:
        self.plainTextEdit.selectAll()
        self.plainTextEdit.copy()

    def onExecuteButtonClicked(self) -> None:
        query = self.plainTextEdit.toPlainText()
        self.model.wikibaseQueryRunner.queueQueryForExecution(query, self.onQueryResult)

    def onQueryResult(self) -> None:
        result = self.model.wikibaseQueryRunner.queryResult
        if not result:
            return
        result = stripUrlPartFromTable(self.model.wikibaseConfig.baseUrl, result)
        table = [[i - 1] + list(row) for (i, row) in enumerate(result)]
        table[0][0] = "rowId"
        self.model.sqlDatabase.addTable("queryResult", table)

        self.tableModel.setTable("queryResult")
        self.tableModel.select()
        self.tableView.hideColumn(0)
        headerResizeNeatly(self.tableView.horizontalHeader())
