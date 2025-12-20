from ..backend.batcheditor import BatchEditor
from ..backend.constraints import ConstraintAnalyzer
from ..backend.wikibasehelper import WikibaseHelper

class Model:
    def __init__(self):
        self.wikibaseHelper = WikibaseHelper()
        self.constraintAnalyzer = ConstraintAnalyzer(self.wikibaseHelper)
        self.batchEditor = BatchEditor(self.wikibaseHelper)
