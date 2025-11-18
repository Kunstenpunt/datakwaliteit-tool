import sys, textwrap

from PySide6.QtCore import QAbstractTableModel, QSortFilterProxyModel, Qt, QUrl
from PySide6.QtGui import QBrush, QDesktopServices, QGuiApplication, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QHeaderView,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from backend.wikibasehelper import BASE_URL, WikibaseHelper
from backend.constraints import ConstraintAnalyzer
from backend.utils import urlFromId

from ui.constrainttab import Ui_ConstraintTab
from ui.mainwindow import Ui_MainWindow
from ui.querytab import Ui_QueryTab


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
            return data

        if role == Qt.ItemDataRole.BackgroundRole:
            data = self._data[index.row() + 1][index.column()]
            if type(data) == type(True):
                return (
                    QBrush(Qt.GlobalColor.darkGreen)
                    if data
                    else QBrush(Qt.GlobalColor.darkRed)
                )

        if role == Qt.ItemDataRole.ForegroundRole:
            data = self._data[index.row() + 1][index.column()]
            if type(data) == type(True):
                return QBrush(Qt.GlobalColor.white)

    def rowCount(self, index):
        return len(self._data) - 1

    def columnCount(self, index):
        return len(self._data[0])

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self._data[0][section]


class Model:
    def __init__(self):
        self.wikibaseHelper = WikibaseHelper()
        self.wikibaseHelper.login()
        self.constraintAnalyzer = ConstraintAnalyzer(self.wikibaseHelper)


class QueryTab(QWidget, Ui_QueryTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model

        self.executeButton.clicked.connect(self.onExecuteButtonClicked)
        self.tableView.doubleClicked.connect(onTableDoubleClicked)

    def onExecuteButtonClicked(self):
        query = self.plainTextEdit.toPlainText()
        result = self.model.wikibaseHelper.executeQuery(query, self.onQueryResult)

    def onQueryResult(self):
        result = self.model.wikibaseHelper.queryResult
        if not result:
            return
        resultModel = QSortFilterProxyModel()
        resultModel.setSourceModel(SimpleTableModel(result))
        self.tableView.setModel(resultModel)
        header = self.tableView.horizontalHeader()
        headerResizeNeatly(header)


class ConstraintsTab(QWidget, Ui_ConstraintTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.validateButton.setEnabled(False)

        self.reloadButton.clicked.connect(self.onReloadButtonClicked)
        self.validateButton.clicked.connect(self.onValidateButtonClicked)
        self.propertiesTableView.doubleClicked.connect(onTableDoubleClicked)
        self.violationsTableView.doubleClicked.connect(onTableDoubleClicked)
        self.model.constraintAnalyzer.constrainedPropertiesUpdated.connect(
            self.onConstrainedPropertiesUpdated
        )
        self.model.constraintAnalyzer.focusedPropertyConstraintUpdated.connect(
            self.onFocusedPropertyConstraintUpdated
        )
        # Automatically perform query for constrainted properties on startup
        self.model.constraintAnalyzer.updateConstraints()

    def onReloadButtonClicked(self):
        self.model.constraintAnalyzer.updateConstraints()

    def onConstrainedPropertiesUpdated(self):
        header = [
            "Prop ID",
            "Prop label",
            "Constraint ID",
            "Constraint Label",
            "Implemented",
        ]
        data = [header] + self.model.constraintAnalyzer.getConstraintsListFull()
        sortableDataModel = QSortFilterProxyModel()
        sortableDataModel.setSourceModel(SimpleTableModel(data))
        self.propertiesTableView.setModel(sortableDataModel)
        header = self.propertiesTableView.horizontalHeader()
        headerResizeNeatly(header)
        self.propertiesTableView.selectionModel().currentChanged.connect(self.onPropertySelectionChanged)

    def onPropertySelectionChanged(self, current, _):
        if current == None:
            return
        tableModel = current.model()
        propId = tableModel.data(tableModel.index(current.row(), 0))
        constraintId = tableModel.data(tableModel.index(current.row(), 2))
        self.model.constraintAnalyzer.setFocusedConstraint(propId, constraintId)

    def onFocusedPropertyConstraintUpdated(self):
        focusedPropertyConstraint = self.model.constraintAnalyzer.focusedConstraint
        focusedPropertyConstraint.violationsUpdated.connect(
            self.updateViolationsTableView
        )
        focusedPropertyConstraint.qualifiersUpdated.connect(
            self.updateFocusedPropertyConstraintLabel
        )
        self.updateFocusedPropertyConstraintLabel()
        self.validateButton.setEnabled(focusedPropertyConstraint.implemented)
        self.updateViolationsTableView()
        focusedPropertyConstraint.queryQualifiers()

    def updateFocusedPropertyConstraintLabel(self):
        focusedPropertyConstraint = self.model.constraintAnalyzer.focusedConstraint
        self.labelRight.setText(focusedPropertyConstraint.pretty())

    def onValidateButtonClicked(self):
        focusedPropertyConstraint = self.model.constraintAnalyzer.focusedConstraint
        focusedPropertyConstraint.queryViolations()

    def updateViolationsTableView(self):
        data = self.model.constraintAnalyzer.focusedConstraint.violations
        if data == None:
            self.violationsTableView.setModel(None)
            return
        sortableDataModel = QSortFilterProxyModel()
        sortableDataModel.setSourceModel(SimpleTableModel(data))
        self.violationsTableView.setModel(sortableDataModel)
        header = self.violationsTableView.horizontalHeader()
        headerResizeNeatly(header)
        header.resizeSection(0, header.defaultSectionSize())


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.model = Model()

        self.tabWidget.addTab(ConstraintsTab(self.model), "Constraints")
        self.tabWidget.addTab(QueryTab(self.model), "Query")
        self.queryIndicator = QProgressBar()
        self.queryIndicator.setRange(0, 0)
        self.queryIndicator.setMaximumWidth(128)
        self.statusbar.addWidget(self.queryIndicator)
        self.queryIndicator.hide()

        self.copyQueryButton = QPushButton()
        self.copyQueryButton.setText("Copy Last Query to Clipboard")
        self.copyQueryButton.clicked.connect(self.copyQueryToClipboard)
        self.statusbar.addPermanentWidget(self.copyQueryButton)

        self.model.wikibaseHelper.queryStarted.connect(self.queryIndicator.show)
        self.model.wikibaseHelper.queryDone.connect(self.queryIndicator.hide)
        self.model.wikibaseHelper.queryDone.connect(self.reportQueryStatus)

    def copyQueryToClipboard(self):
        query = textwrap.dedent(self.model.wikibaseHelper.mostRecentQuery).lstrip()
        clipboard = QGuiApplication.clipboard()
        if not "PREFIX" in query:
            prefixes = textwrap.dedent(self.model.wikibaseHelper.queryPrefixes).lstrip()
            query = f"{prefixes}\n{query}"
        clipboard.setText(query)

    def reportQueryStatus(self):
        if self.model.wikibaseHelper.queryResult == None:
            self.statusbar.showMessage("LAST QUERY FAILED!")
        else:
            self.statusbar.clearMessage()


app = QApplication(sys.argv)
w = MainWindow()
w.show()
app.exec()
