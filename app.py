import sys, textwrap

from PySide6.QtCore import (
    QAbstractTableModel,
    QFileInfo,
    QSortFilterProxyModel,
    QStandardPaths,
    Qt,
    QUrl,
)
from PySide6.QtGui import QBrush, QDesktopServices, QGuiApplication, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
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
from backend.export import exportMultipleConstraintsToOds, exportSingleConstraintToOds
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

    def setData(self, index, value, role=None):
        self._data[index.row() + 1][index.column()] = value
        self.dataChanged.emit(index, index)
        return True


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
        self.exportDir = QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.DocumentsLocation,
        )
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        self.validateButton.setEnabled(False)
        self.exportButton.setEnabled(False)

        self.reloadButton.clicked.connect(self.onReloadButtonClicked)
        self.validateAllButton.clicked.connect(self.validateAll)
        self.validateButton.clicked.connect(self.onValidateButtonClicked)
        self.exportAllButton.clicked.connect(self.exportAllValidated)
        self.exportButton.clicked.connect(self.exportSingleConstraint)
        self.propertiesTableView.doubleClicked.connect(onTableDoubleClicked)
        self.violationsTableView.doubleClicked.connect(onTableDoubleClicked)
        self.model.constraintAnalyzer.constrainedPropertiesUpdated.connect(
            self.onConstrainedPropertiesUpdated
        )
        self.model.constraintAnalyzer.constrainedPropertyValidated.connect(
            self.onConstrainedPropertyValidated
        )
        self.model.constraintAnalyzer.focusedPropertyConstraintUpdated.connect(
            self.onFocusedPropertyConstraintUpdated
        )
        self.model.constraintAnalyzer.validateAllDone.connect(
            self.updateValidateAllLabel
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
            "Validated",
        ]
        data = [header] + self.model.constraintAnalyzer.getConstraintsListFull()
        sortableDataModel = QSortFilterProxyModel()
        sortableDataModel.setSourceModel(SimpleTableModel(data))
        self.propertiesTableView.setModel(sortableDataModel)
        header = self.propertiesTableView.horizontalHeader()
        headerResizeNeatly(header)
        self.propertiesTableView.selectionModel().currentChanged.connect(
            self.onPropertySelectionChanged
        )

    def onConstrainedPropertyValidated(self):
        data = self.model.constraintAnalyzer.getConstraintsListFull()
        model = self.propertiesTableView.model().sourceModel()
        validatedColumnIndex = 5
        for rowIndex, row in enumerate(data):
            model.setData(model.index(rowIndex, validatedColumnIndex), row[5])

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

    def validateAll(self):
        if not self.model.constraintAnalyzer.validatingAll():
            self.model.constraintAnalyzer.validateAll()
        else:
            self.model.constraintAnalyzer.stopValidatingAll()
        self.updateValidateAllLabel()

    def updateValidateAllLabel(self):
        self.validateAllButton.setText(
            "Stop Validating All"
            if self.model.constraintAnalyzer.validatingAll()
            else "Validate All"
        )

    def onValidateButtonClicked(self):
        focusedPropertyConstraint = self.model.constraintAnalyzer.focusedConstraint
        if focusedPropertyConstraint.qualifiersObtained:
            focusedPropertyConstraint.queryViolations()
        else:
            focusedPropertyConstraint.queryQualifiers()

    def updateViolationsTableView(self):
        data = self.model.constraintAnalyzer.focusedConstraint.violations
        self.exportButton.setEnabled(data != None)
        if data == None:
            self.violationsTableView.setModel(None)
            return
        sortableDataModel = QSortFilterProxyModel()
        sortableDataModel.setSourceModel(SimpleTableModel(data))
        self.violationsTableView.setModel(sortableDataModel)
        header = self.violationsTableView.horizontalHeader()
        headerResizeNeatly(header)
        header.resizeSection(0, header.defaultSectionSize())

    def exportSingleConstraint(self):
        constraint = self.model.constraintAnalyzer.focusedConstraint
        defaultFileName = f"constraint_violations_{constraint.property.identifier}_{constraint.identifier}.ods"
        fileName = QFileDialog.getSaveFileName(
            self,
            f"Export Violations for {constraint.property.identifier}-{constraint.identifier}",
            f"{self.exportDir}/{defaultFileName}",
            "ODS files (*.ods)",
        )[0]
        if not fileName:
            return
        self.exportDir = QFileInfo(fileName).absolutePath()
        exportUrl = self.exportUrlCheckBox.isChecked()
        exportSingleConstraintToOds(constraint, fileName, exportUrl)

    def exportAllValidated(self):
        validatedConstraints = sorted(
            [
                c
                for c in self.model.constraintAnalyzer.constraints.values()
                if c.violations != None
            ]
        )
        defaultFileName = "constraint_violations_combined.ods"
        fileName = QFileDialog.getSaveFileName(
            self,
            "Export Violations for All Validated Constraints",
            f"{self.exportDir}/{defaultFileName}",
            "ODS files (*.ods)",
        )[0]
        if not fileName:
            return
        self.exportDir = QFileInfo(fileName).absolutePath()
        exportUrl = self.exportAllUrlCheckBox.isChecked()
        exportMultipleConstraintsToOds(validatedConstraints, fileName, exportUrl)


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
