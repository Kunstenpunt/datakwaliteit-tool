from ..backend.wikibasehelper import WikibaseHelper
from ..backend.constraints import ConstraintAnalyzer


class Model:
    def __init__(self):
        self.wikibaseHelper = WikibaseHelper()
        self.constraintAnalyzer = ConstraintAnalyzer(self.wikibaseHelper)
