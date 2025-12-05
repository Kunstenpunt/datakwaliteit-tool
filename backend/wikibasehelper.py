from PySide6.QtCore import Signal, QObject, QThread

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config
from wikibaseintegrator.wbi_helpers import execute_sparql_query
from wikibaseintegrator.wbi_login import Login

from .utils import queryResultToList

BASE_URL = "https://kg.kunsten.be"


class QueryWorker(QObject):
    finished = Signal()

    def __init__(self, query, prefixes):
        super().__init__()
        self.query = query
        self.prefixes = None if "PREFIX" in query else prefixes
        self.resultList = None

    def run(self):
        result = None
        try:
            result = execute_sparql_query(
                self.query, self.prefixes, max_retries=1, retry_after=1
            )
        except Exception as e:
            print(e)
        self.resultList = queryResultToList(result)
        self.finished.emit()


class WikibaseHelper(QObject):
    queryStarted = Signal()  # For loading indicator
    queryDone = Signal()  # For loading indicator
    _queryResultAvailable = Signal()
    _readyForNewQuery = Signal()

    def __init__(self):
        super().__init__()

        # The necessary configuration for the wikibase instance of Kunstenpunt
        config["DEFAULT_LANGUAGE"] = "nl"
        config["WIKIBASE_URL"] = "https://kg.kunsten.be"
        config["MEDIAWIKI_API_URL"] = "https://kg.kunsten.be/w/api.php"
        config["MEDIAWIKI_INDEX_URL"] = "https://kg.kunsten.be/w/index.php"
        config["MEDIAWIKI_REST_URL"] = "https://kg.kunsten.be/w/rest.php"
        config["SPARQL_ENDPOINT_URL"] = (
            "https://kg.kunsten.be/query/proxy/wdqs/bigdata/namespace/wdq/sparql"
        )
        # All used prefixes to keep queries in other code more lean looking
        self.queryPrefixes = """
            PREFIX kp:<https://kg.kunsten.be/entity/>
            PREFIX kpt:<https://kg.kunsten.be/prop/direct/>
            PREFIX kpp:<https://kg.kunsten.be/prop/>
            PREFIX kpps:<https://kg.kunsten.be/prop/statement/>
            PREFIX kppq:<https://kg.kunsten.be/prop/qualifier/>
        """

        self.executingQuery = False
        self.mostRecentQuery = None
        self.queryQueue = []
        self.queryResult = None

        self._readyForNewQuery.connect(self.handleQueryQueue)

        wbi = WikibaseIntegrator()

    def executeQuery(self, queryString, callback):
        self.queryQueue.append((queryString, callback))
        if len(self.queryQueue) == 1 and not self.executingQuery:
            self.handleQueryQueue()
        
    def handleQueryQueue(self):
        if not self.queryQueue:
            return
        (queryString, callback) = self.queryQueue.pop(0)
        self.processQuery(queryString, callback)

    def processQuery(self, queryString, callback):
        if self.executingQuery:
            return
        else:
            self.executingQuery = True

        try:
            self._queryResultAvailable.disconnect()
        except TypeError:
            pass

        self._queryResultAvailable.connect(callback)

        self.queryThread = QThread()
        self.queryWorker = QueryWorker(queryString, self.queryPrefixes)
        self.queryWorker.moveToThread(self.queryThread)
        self.queryThread.started.connect(self.queryWorker.run)
        self.queryWorker.finished.connect(self.queryWorkerFinished)
        self.queryWorker.finished.connect(self.queryThread.quit)
        self.queryWorker.finished.connect(self.queryWorker.deleteLater)
        self.queryThread.finished.connect(self.queryThread.deleteLater)
        self.queryThread.destroyed.connect(self.queryThreadDestroyed)

        self.mostRecentQuery = queryString
        self.queryStarted.emit()
        self.queryThread.start()

    def queryWorkerFinished(self):
        self.queryResult = self.queryWorker.resultList
        self._queryResultAvailable.emit()
        self.queryDone.emit()

    def queryThreadDestroyed(self):
        self.executingQuery = False
        self._readyForNewQuery.emit()
