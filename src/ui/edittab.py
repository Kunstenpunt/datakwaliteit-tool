from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget

from .designer.edittab import Ui_EditTab


class EditTab(QWidget, Ui_EditTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model

        self.statementsPlainTextEdit.setFont(QFont("monospace"))

        self.copyButton.clicked.connect(self.copyQuery)
        self.copyStatementsButton.clicked.connect(self.copyStatements)
        self.generateButton.clicked.connect(self.generateBatchStatements)
        self.model.batchEditor.statementGenerationDone.connect(
            self.updateBatchStatements
        )

    def copyQuery(self):
        self.queryPlainTextEdit.selectAll()
        self.queryPlainTextEdit.copy()

    def copyStatements(self):
        self.statementsPlainTextEdit.selectAll()
        self.statementsPlainTextEdit.copy()

    def generateBatchStatements(self):
        query = self.queryPlainTextEdit.toPlainText()
        recipe = self.recipePlainTextEdit.toPlainText()
        self.model.batchEditor.startPipeline(query, recipe)

    def updateBatchStatements(self):
        self.statementsPlainTextEdit.setPlainText(
            self.model.batchEditor.generatedStatements
        )
