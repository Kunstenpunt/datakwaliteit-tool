import textwrap

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QMainWindow,
    QProgressBar,
    QPushButton,
)

from .backend.model import Model
from .ui.constrainttab import ConstraintsTab
from .ui.edittab import EditTab
from .ui.querytab import QueryTab

from .ui.designer.mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.model = Model()

        self.tabWidget.addTab(ConstraintsTab(self.model), "Constraints")
        self.tabWidget.addTab(QueryTab(self.model), "Query")
        self.tabWidget.addTab(EditTab(self.model), "Edit")
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
