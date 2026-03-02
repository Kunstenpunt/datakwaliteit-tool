from .batcheditor import BatchEditor
from .configuration import ConfigHandler
from .constraint.model import ConstraintCheckModel
from .constraint.queries import QueryBuilder
from .wikibasehelper import WikibaseConfig, WikibaseQueryRunner


class Model:
    def __init__(self) -> None:
        self.configHandler = ConfigHandler()
        self.wikibaseConfig = WikibaseConfig(self.configHandler)
        self.queryBuilder = QueryBuilder(self.wikibaseConfig)
        self.wikibaseQueryRunner = WikibaseQueryRunner(self.wikibaseConfig)
        self.constraintCheckModel = ConstraintCheckModel(
            self.queryBuilder, self.wikibaseConfig, self.wikibaseQueryRunner
        )
        self.batchEditor = BatchEditor(self.wikibaseConfig, self.wikibaseQueryRunner)
