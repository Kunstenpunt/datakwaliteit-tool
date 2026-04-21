from .batcheditor import BatchEditor
from .configuration import ConfigHandler
from .constraint.model import ConstraintCheckModel
from .constraint.queries import QueryBuilder
from .sql import SqlDatabase
from .wikibasehelper import WikibaseConfig, WikibaseEditor, WikibaseQueryRunner


class Model:
    def __init__(self) -> None:
        self.configHandler = ConfigHandler()
        self.wikibaseConfig = WikibaseConfig(self.configHandler)
        self.queryBuilder = QueryBuilder(self.wikibaseConfig)
        self.wikibaseQueryRunner = WikibaseQueryRunner(self.wikibaseConfig)
        self.wikibaseEditor = WikibaseEditor(self.wikibaseConfig)
        self.sqlDatabase = SqlDatabase()
        self.constraintCheckModel = ConstraintCheckModel(
            self.queryBuilder,
            self.sqlDatabase,
            self.wikibaseConfig,
            self.wikibaseQueryRunner,
        )
        self.batchEditor = BatchEditor(self.wikibaseConfig, self.wikibaseQueryRunner)
