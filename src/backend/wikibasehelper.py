from PySide6.QtCore import Signal, QObject, QThread

from wikibaseintegrator import WikibaseIntegrator
from wikibaseintegrator.wbi_config import config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

from .configuration import ExtraWikibaseKey, WbiConfigKey
from .utils import queryResultToList


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

    def __init__(self, configuration):
        super().__init__()

        self._configuration = configuration
        wbiConfigPairs = self._configuration.getWikibaseConfig()
        allWbiKeysObtained = True
        for key in WbiConfigKey:
            value = wbiConfigPairs.get(key)
            if value:
                config[key] = value
            else:
                allWbiKeysObtained = False
            
        
        self._instanceOfPid = wbiConfigPairs.get(ExtraWikibaseKey.INSTANCE_OF_PID)
        self._subclassOfPid = wbiConfigPairs.get(ExtraWikibaseKey.SUBCLASS_OF_PID)

        # The necessary configuration for the wikibase instance of Kunstenpunt
        # config[WbiConfigKey.DEFAULT_LANGUAGE] = "nl"
        # config[WbiConfigKey.WIKIBASE_URL] = "https://kg.kunsten.be"
        # config[WbiConfigKey.MEDIAWIKI_API_URL] = "https://kg.kunsten.be/w/api.php"
        # config[WbiConfigKey.MEDIAWIKI_INDEX_URL] = "https://kg.kunsten.be/w/index.php"
        # config[WbiConfigKey.MEDIAWIKI_REST_URL] = "https://kg.kunsten.be/w/rest.php"
        # config[WbiConfigKey.SPARQL_ENDPOINT_URL] = (
        #     "https://kg.kunsten.be/query/proxy/wdqs/bigdata/namespace/wdq/sparql"
        # )
        # config[WbiConfigKey.PROPERTY_CONSTRAINT_PID] = "P85"

        if not allWbiKeysObtained:
            self._configuration.setWikibaseConfig(config)
        # All used prefixes to keep queries in other code more lean looking
        self.queryPrefixes = f"""
            PREFIX kp:<{ config[WbiConfigKey.WIKIBASE_URL] }/entity/>
            PREFIX kpt:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/direct/>
            PREFIX kpp:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/>
            PREFIX kpps:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/statement/>
            PREFIX kppq:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/qualifier/>
        """

        self.executingQuery = False
        self.mostRecentQuery = None
        self.queryQueue = []
        self.queryResult = None
        self.queryThread = None
        self.queryWorker = None

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

    def getPropertyConstraintPid(self):
        return config[WbiConfigKey.PROPERTY_CONSTRAINT_PID]

    def getDefaultLanguage(self):
        return config[WbiConfigKey.DEFAULT_LANGUAGE]
    
    def getBaseUrl(self):
        return config[WbiConfigKey.WIKIBASE_URL]

    def getPureUrl(self):
        return config[WbiConfigKey.WIKIBASE_URL].replace("https://", "").replace("http://", "")
    
    def getInstanceOfPid(self):
        return self._instanceOfPid
    
    def getSubclassOfPid(self):
        return self._subclassOfPid
