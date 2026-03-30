import textwrap

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import (
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
)

from .backend.model import Model
from .ui.configurationtab import ConfigurationTab
from .ui.constrainttab import ConstraintsTab
from .ui.edittab import EditTab
from .ui.querytab import QueryTab

from .ui.designer.mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setupUi(self)  # type: ignore

        self.model = Model()

        self.tabWidget.addTab(ConstraintsTab(self.model), "Constraints")
        self.tabWidget.addTab(QueryTab(self.model), "Query")
        self.tabWidget.addTab(EditTab(self.model), "Edit")
        self.configurationTabIndex = self.tabWidget.addTab(
            ConfigurationTab(self.model), "Configuration"
        )
        self.tabWidget.currentChanged.connect(self._onCurrentTabChanged)
        self.queryIndicator = QProgressBar()
        self.queryIndicator.setRange(0, 0)
        self.queryIndicator.setMaximumWidth(128)
        self.statusbar.addWidget(self.queryIndicator)
        self.queryIndicator.hide()
        self.queryIndicatorLabel = QLabel()
        self.statusbar.addWidget(self.queryIndicatorLabel)

        self.copyQueryButton = QPushButton()
        self.copyQueryButton.setText("Copy Last Query to Clipboard")
        self.copyQueryButton.clicked.connect(self.copyQueryToClipboard)
        self.statusbar.addPermanentWidget(self.copyQueryButton)

        self.model.wikibaseQueryRunner.queryStarted.connect(self.onQueryStarted)
        self.model.wikibaseQueryRunner.queryDone.connect(self.onQueryDone)

        # Load constrained properties on startup
        self.model.constraintCheckModel.queryConstraints()

    def onQueryStarted(self) -> None:
        self.queryIndicator.show()
        self.queryIndicatorLabel.setText("Running query...")

    def onQueryDone(self) -> None:
        self.queryIndicator.hide()
        self.queryIndicatorLabel.setText(
            "LAST QUERY FAILED"
            if self.model.wikibaseQueryRunner.queryResult == None
            else ""
        )

    def _onCurrentTabChanged(self, index: int) -> None:
        if index == self.configurationTabIndex:
            pass

    def copyQueryToClipboard(self) -> None:
        query = textwrap.dedent(self.model.wikibaseQueryRunner.mostRecentQuery).lstrip()
        clipboard = QGuiApplication.clipboard()
        if not "PREFIX" in query:
            prefixes = textwrap.dedent(
                self.model.wikibaseQueryRunner.queryPrefixes
            ).lstrip()
            query = f"{prefixes}\n{query}"
        clipboard.setText(query)
