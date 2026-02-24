import re
from typing import Optional, Sequence

from PySide6.QtCore import QObject, Signal

from .types import Table
from .utils import stripUrlPartFromTable
from .wikibasehelper import WikibaseConfig, WikibaseQueryRunner


class BatchEditor(QObject):

    statementGenerationDone = Signal()

    def __init__(
        self, wikibaseConfig: WikibaseConfig, wikibaseQueryRunner: WikibaseQueryRunner
    ) -> None:
        super().__init__()

        self.wikibaseConfig = wikibaseConfig
        self.wikibaseQueryRunner = wikibaseQueryRunner

        self.inputData: Optional[Table[str]] = None
        self.query = ""
        self.recipe = ""
        self.generatedStatements = ""

    def startPipeline(self, query: str, recipe: str) -> None:
        self.query = query
        self.recipe = recipe
        self._sanitizeRecipe()

        self.wikibaseQueryRunner.queueQueryForExecution(
            self.query, self._executeQueryResult
        )

    def _sanitizeRecipe(self) -> None:
        # Each command is in a new line or separated by "||"
        recipeSplit = re.split(r"\n|\|\|", self.recipe)
        recipe = [step.strip() for step in recipeSplit]
        recipe = [step for step in recipe if step != ""]
        cleanRecipe = []
        for step in recipe:
            step = re.split(r"\t|\|", step)
            step = [token.strip() for token in step]
            step = [token for token in step if token != ""]
            step = "\t".join(step)
            cleanRecipe.append(step)
        self.recipe = "\n".join(cleanRecipe)

    def _executeQueryResult(self) -> None:
        self.inputData = self.wikibaseQueryRunner.queryResult
        self._generateEditStatements()

    def _generateEditStatements(self) -> None:
        if not self.inputData:
            return

        self.inputData = stripUrlPartFromTable(
            self.wikibaseConfig.getBaseUrl(), self.inputData
        )

        recipeFormatStr = self._generateRecipeFormatStr(self.inputData[0])
        self._applyRecipeFormatStr(recipeFormatStr)

        self.statementGenerationDone.emit()

    def _generateRecipeFormatStr(self, header: Sequence[str]) -> str:
        recipeFormatStr = self.recipe
        # Sort from long to short to make sure we do not replace substrings of variable names.
        headerSorted = sorted(enumerate(header), key=lambda i: len(i[1]), reverse=True)
        for i, varName in headerSorted:
            recipeFormatStr = recipeFormatStr.replace("?" + varName, f"{{{i}}}")
        return recipeFormatStr

    def _applyRecipeFormatStr(self, recipeFormatStr):
        result = []
        for row in self.inputData[1:]:
            result += [recipeFormatStr.format(*row)]

        self.generatedStatements = "\n".join(result)
