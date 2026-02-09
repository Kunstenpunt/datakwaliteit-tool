from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget

from ..backend.model import Model

from .designer.edittab import Ui_EditTab


class EditTab(QWidget, Ui_EditTab):
    def __init__(self, model: Model) -> None:
        super().__init__()
        self.setupUi(self)  # type: ignore

        self.model = model

        self.statementsPlainTextEdit.setFont(QFont("monospace"))

        self.copyButton.clicked.connect(self.copyQuery)
        self.copyStatementsButton.clicked.connect(self.copyStatements)
        self.generateButton.clicked.connect(self.generateBatchStatements)
        self.model.batchEditor.statementGenerationDone.connect(
            self.updateBatchStatements
        )

    def copyQuery(self) -> None:
        self.queryPlainTextEdit.selectAll()
        self.queryPlainTextEdit.copy()

    def copyStatements(self) -> None:
        self.statementsPlainTextEdit.selectAll()
        self.statementsPlainTextEdit.copy()

    def generateBatchStatements(self) -> None:
        query = self.queryPlainTextEdit.toPlainText()
        recipe = self.recipePlainTextEdit.toPlainText()
        self.model.batchEditor.startPipeline(query, recipe)

    def updateBatchStatements(self) -> None:
        self.statementsPlainTextEdit.setPlainText(
            self.model.batchEditor.generatedStatements
        )
