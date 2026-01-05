import re

from PySide6.QtCore import QObject, Signal

from .utils import stripUrlPartFromTable
from .wikibasehelper import BASE_URL


class BatchEditor(QObject):

    inputDataObtained = Signal()
    statementGenerationDone = Signal()

    def __init__(self, wikibaseHelper):
        super().__init__()

        self.wikibaseHelper = wikibaseHelper

        self.inputData = None
        self.query = None
        self.recipe = None
        self.generatedStatements = None

        self.inputDataObtained.connect(self._generateEditStatements)

    def startPipeline(self, query, recipe):
        self.query = query
        self.recipe = recipe
        self._sanitizeRecipe()

        self.wikibaseHelper.executeQuery(self.query, self._executeQueryResult)

    def _sanitizeRecipe(self):
        # Each command is in a new line or separated by "||"
        recipeSplit = re.split(r"\n|\|\|", self.recipe)
        recipe = [step.strip() for step in recipeSplit]
        recipe = [step for step in recipe if step != ""]
        self.recipe = []
        for step in recipe:
            step = re.split(r"\t|\|", step)
            step = [token.strip() for token in step]
            step = [token for token in step if token != ""]
            step = "\t".join(step)
            self.recipe.append(step)
        self.recipe = "\n".join(self.recipe)

    def _executeQueryResult(self):
        self.inputData = self.wikibaseHelper.queryResult
        self.inputDataObtained.emit()

    def _generateEditStatements(self):
        result = []
        if type(self.inputData) != list or len(self.inputData) == 0:
            return

        self.inputData = stripUrlPartFromTable(BASE_URL, self.inputData)
        recipeFormatStr = self._prepareRecipeFormatStr(self.inputData[0])

        for row in self.inputData[1:]:
            result += [recipeFormatStr.format(*row)]

        self.generatedStatements = "\n".join(result)
        self.statementGenerationDone.emit()

    def _prepareRecipeFormatStr(self, header):
        recipeFormatStr = self.recipe
        for i, varName in enumerate(header):
            recipeFormatStr = recipeFormatStr.replace("?" + varName, f"{{{i}}}")
        return recipeFormatStr
