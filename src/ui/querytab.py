from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtWidgets import QWidget

from ..backend.model import Model
from ..backend.utils import stripUrlPartFromTable

from .designer.querytab import Ui_QueryTab
from .simpletablemodel import (
    headerResizeNeatly,
    SimpleTableModel,
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
        result = stripUrlPartFromTable(self.model.wikibaseConfig.getBaseUrl(), result)
        resultModel = QSortFilterProxyModel()
        resultModel.setSourceModel(SimpleTableModel(result))
        self.tableView.setModel(resultModel)
        header = self.tableView.horizontalHeader()
        headerResizeNeatly(header)
