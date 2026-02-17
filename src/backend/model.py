from .batcheditor import BatchEditor
from .configuration import ConfigHandler
from .constraints import ConstraintAnalyzer
from .wikibasehelper import WikibaseConfig, WikibaseQueryRunner


class Model:
    def __init__(self) -> None:
        self.configHandler = ConfigHandler()
        self.wikibaseConfig = WikibaseConfig(self.configHandler)
        self.wikibaseQueryRunner = WikibaseQueryRunner(self.wikibaseConfig)
        self.constraintAnalyzer = ConstraintAnalyzer(
            self.wikibaseConfig, self.wikibaseQueryRunner
        )
        self.batchEditor = BatchEditor(self.wikibaseConfig, self.wikibaseQueryRunner)
