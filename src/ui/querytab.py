from PySide6.QtCore import QSortFilterProxyModel
from PySide6.QtWidgets import QWidget

from ..backend.utils import stripUrlPartFromTable
from ..backend.wikibasehelper import BASE_URL

from .designer.querytab import Ui_QueryTab
from .simpletablemodel import headerResizeNeatly, onTableDoubleClicked, SimpleTableModel


class QueryTab(QWidget, Ui_QueryTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model

        self.executeButton.clicked.connect(self.onExecuteButtonClicked)
        self.tableView.doubleClicked.connect(onTableDoubleClicked)

    def onExecuteButtonClicked(self):
        query = self.plainTextEdit.toPlainText()
        self.model.wikibaseHelper.executeQuery(query, self.onQueryResult)

    def onQueryResult(self):
        result = self.model.wikibaseHelper.queryResult
        if not result:
            return
        result = stripUrlPartFromTable(BASE_URL, result)
        resultModel = QSortFilterProxyModel()
        resultModel.setSourceModel(SimpleTableModel(result))
        self.tableView.setModel(resultModel)
        header = self.tableView.horizontalHeader()
        headerResizeNeatly(header)
