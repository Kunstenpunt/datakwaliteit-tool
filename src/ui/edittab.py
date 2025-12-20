from PySide6.QtWidgets import QWidget

from .designer.edittab import Ui_EditTab


class EditTab(QWidget, Ui_EditTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model

        self.generateButton.clicked.connect(self.generateBatchStatements)
        self.model.batchEditor.statementGenerationDone.connect(
            self.updateBatchStatements
        )

    def generateBatchStatements(self):
        query = self.queryPlainTextEdit.toPlainText()
        recipe = self.recipePlainTextEdit.toPlainText()
        self.model.batchEditor.startPipeline(query, recipe)

    def updateBatchStatements(self):
        self.statementsPlainTextEdit.setPlainText(
            self.model.batchEditor.generatedStatements
        )
