from .batcheditor import BatchEditor
from .configuration import Configuration
from .constraints import ConstraintAnalyzer
from .wikibasehelper import WikibaseHelper


class Model:
    def __init__(self):
        self.configuration = Configuration()
        self.wikibaseHelper = WikibaseHelper(self.configuration)
        self.constraintAnalyzer = ConstraintAnalyzer(self.wikibaseHelper)
        self.batchEditor = BatchEditor(self.wikibaseHelper)
