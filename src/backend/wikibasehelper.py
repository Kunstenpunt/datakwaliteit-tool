from typing import Callable, Optional, Sequence

from PySide6.QtCore import Signal, QMetaObject, QObject, QThread

from wikibaseintegrator.wbi_config import config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

from .configuration import Configuration, ExtraWikibaseKey, WbiConfigKey
from .utils import queryResultToList, stringOrDefault


class QueryWorker(QThread):
    resultReady = Signal()

    def __init__(self, parent: QObject, query: str, prefixes: str) -> None:
        super().__init__(parent)
        self.query = query
        self.prefixes = None if "PREFIX" in query else prefixes
        self.resultList: Optional[Sequence[Sequence[str]]] = None

    def run(self) -> None:
        result = None
        try:
            result = execute_sparql_query(
                self.query, self.prefixes, max_retries=1, retry_after=1
            )
        except Exception as e:
            print(e)
        self.resultList = queryResultToList(result)
        self.resultReady.emit()


class WikibaseHelper(QObject):
    queryStarted = Signal()  # For loading indicator
    queryDone = Signal()  # For loading indicator
    _queryResultAvailable = Signal()
    _readyForNewQuery = Signal()

    def __init__(self, configuration: Configuration) -> None:
        super().__init__()

        self._configuration = configuration
        self._instanceOfPid = ""
        self._subclassOfPid = ""

        self.callbackConnection: Optional[QMetaObject.Connection] = None
        self.callbackData: Optional[object] = None
        self.executingQuery = False
        self.mostRecentQuery = ""
        self.queryQueue: list[tuple[str, Callable[[], None], object]] = []
        self.queryResult: Optional[Sequence[Sequence[str]]] = None

        self._configuration.wbiConfigChanged.connect(self.loadWbiConfig)
        self.loadWbiConfig()
        self._configuration.extraWikibaseConfigChanged.connect(
            self.loadExtraWikibaseConfig
        )
        self.loadExtraWikibaseConfig()

        self._readyForNewQuery.connect(self.handleQueryQueue)

    def loadWbiConfig(self) -> None:
        wbiConfigPairs = self._configuration.getWikibaseConfig()
        allWbiKeysObtained = True
        for key in WbiConfigKey:
            value = wbiConfigPairs.get(key)
            if value:
                config[key] = value
            else:
                allWbiKeysObtained = False

        # This will cause this function to be called again, but only once as then all keys will be obtained.
        if not allWbiKeysObtained:
            self._configuration.setWikibaseConfig(config)
            return

        # All used prefixes to keep queries in other code more lean looking
        self.queryPrefixes = f"""
            PREFIX kp:<{ config[WbiConfigKey.WIKIBASE_URL] }/entity/>
            PREFIX kpt:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/direct/>
            PREFIX kpp:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/>
            PREFIX kpps:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/statement/>
            PREFIX kppq:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/qualifier/>
        """

        # Clear the query queue now that the config has changed.
        self.queryQueue = []

    def loadExtraWikibaseConfig(self) -> None:
        wbiConfigPairs = self._configuration.getWikibaseConfig()

        self._instanceOfPid = wbiConfigPairs.get(ExtraWikibaseKey.INSTANCE_OF_PID, "")
        self._subclassOfPid = wbiConfigPairs.get(ExtraWikibaseKey.SUBCLASS_OF_PID, "")

        # Clear the query queue now that the config has changed.
        self.queryQueue = []

    def executeQuery(
        self, queryString: str, callback: Callable[[], None], data: object = None
    ) -> None:
        self.queryQueue.append((queryString, callback, data))
        if len(self.queryQueue) == 1 and not self.executingQuery:
            self.handleQueryQueue()

    def handleQueryQueue(self) -> None:
        if not self.queryQueue:
            return
        (queryString, callback, data) = self.queryQueue.pop(0)
        self.processQuery(queryString, callback, data)

    def processQuery(
        self, queryString: str, callback: Callable[[], None], data: object
    ) -> None:
        if self.executingQuery:
            return
        else:
            self.executingQuery = True

        if self.callbackConnection:
            self._queryResultAvailable.disconnect(self.callbackConnection)

        self.callbackConnection = self._queryResultAvailable.connect(callback)

        self.callbackData = data

        self.queryWorker = QueryWorker(self, queryString, self.queryPrefixes)
        self.queryWorker.resultReady.connect(self.queryWorkerResultReady)
        self.queryWorker.finished.connect(self.queryWorker.deleteLater)
        self.queryWorker.destroyed.connect(self.queryWorkerDestroyed)

        self.mostRecentQuery = queryString
        self.queryStarted.emit()
        self.queryWorker.start()

    def queryWorkerResultReady(self) -> None:
        self.queryResult = self.queryWorker.resultList
        self._queryResultAvailable.emit()
        self.queryDone.emit()

    def queryWorkerDestroyed(self) -> None:
        self.executingQuery = False
        self._readyForNewQuery.emit()

    def getPropertyConstraintPid(self) -> str:
        return stringOrDefault(config[WbiConfigKey.PROPERTY_CONSTRAINT_PID])

    def getDefaultLanguage(self) -> str:
        return stringOrDefault(config[WbiConfigKey.DEFAULT_LANGUAGE])

    def getBaseUrl(self) -> str:
        return stringOrDefault(config[WbiConfigKey.WIKIBASE_URL])

    def getPureUrl(self) -> str:
        return (
            stringOrDefault(config[WbiConfigKey.WIKIBASE_URL])
            .replace("https://", "")
            .replace("http://", "")
        )

    def getInstanceOfPid(self) -> str:
        return self._instanceOfPid

    def getSubclassOfPid(self) -> str:
        return self._subclassOfPid
