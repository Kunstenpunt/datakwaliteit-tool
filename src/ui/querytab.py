from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtWidgets import QWidget

from ..backend.utils import stripUrlPartFromTable

from .designer.querytab import Ui_QueryTab
from .simpletablemodel import headerResizeNeatly, SimpleTableModel, TableClickHandler


class QueryTab(QWidget, Ui_QueryTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model

        self.copyButton.clicked.connect(self.copy)
        self.executeButton.clicked.connect(self.onExecuteButtonClicked)
        self.tableClickHandler = TableClickHandler(
            self.model.wikibaseHelper.getBaseUrl()
        )
        self.tableView.doubleClicked.connect(
            self.tableClickHandler.onTableDoubleClicked
        )

    def copy(self):
        self.plainTextEdit.selectAll()
        self.plainTextEdit.copy()

    def onExecuteButtonClicked(self):
        query = self.plainTextEdit.toPlainText()
        self.model.wikibaseHelper.executeQuery(query, self.onQueryResult)

    def onQueryResult(self):
        result = self.model.wikibaseHelper.queryResult
        if not result:
            return
        result = stripUrlPartFromTable(self.model.wikibaseHelper.getBaseUrl(), result)
        resultModel = QSortFilterProxyModel()
        resultModel.setSourceModel(SimpleTableModel(result))
        self.tableView.setModel(resultModel)
        header = self.tableView.horizontalHeader()
        headerResizeNeatly(header)
