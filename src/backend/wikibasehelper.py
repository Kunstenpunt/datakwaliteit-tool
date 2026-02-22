import re
from typing import Any, Callable, Optional

from PySide6.QtCore import Signal, QMetaObject, QObject, QThread

from wikibaseintegrator.wbi_config import config
from wikibaseintegrator.wbi_helpers import execute_sparql_query

from .configuration import ConfigHandler, ExtraWikibaseConfigKey, WbiConfigKey
from .types import Table
from .utils import queryResultToTable, stringOrDefault


class WikibaseConfig(QObject):
    wikibaseConfigChanged = Signal()

    def __init__(self, configHandler: ConfigHandler) -> None:
        super().__init__()

        self._configHandler = configHandler
        self._instanceOfPid = ""
        self._subclassOfPid = ""

        self._configHandler.configChanged.connect(self._loadWikibaseConfig)
        self._loadWikibaseConfig()

    def _loadWikibaseConfig(self) -> None:
        wbiConfigPairs = self._configHandler.getWikibaseConfigPairs()
        allWbiKeysObtained = True
        for key in WbiConfigKey:
            value = wbiConfigPairs.get(key)
            if value:
                config[key] = value
            else:
                allWbiKeysObtained = False

        # This will cause this function to be called again, but only once as then all keys will be obtained.
        if not allWbiKeysObtained:
            self._configHandler.setWikibaseConfigPairs(config)
            return

        self._instanceOfPid = stringOrDefault(
            wbiConfigPairs.get(ExtraWikibaseConfigKey.INSTANCE_OF_PID, "")
        )
        self._subclassOfPid = stringOrDefault(
            wbiConfigPairs.get(ExtraWikibaseConfigKey.SUBCLASS_OF_PID, "")
        )
        
        self.wikibaseConfigChanged.emit()

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


class QueryThread(QThread):
    resultReady = Signal()

    _prefixPattern = re.compile(r"^\s*PREFIX", re.MULTILINE)

    def __init__(self, parent: QObject, query: str, defaultPrefixes: str) -> None:
        super().__init__(parent)
        self._query = query
        self._prefixes = None if self.prefixesPresentInQuery() else defaultPrefixes
        self.resultTable: Optional[Table[str]] = None

    def prefixesPresentInQuery(self) -> bool:
        return bool(self._prefixPattern.search(self._query))

    def run(self) -> None:
        result = self._executeQuery()
        self.resultTable = queryResultToTable(result)
        self.resultReady.emit()

    def _executeQuery(self) -> Any:
        try:
            return execute_sparql_query(
                self._query, self._prefixes, max_retries=1, retry_after=1
            )
        except Exception as e:
            print(e)
            return None


class WikibaseQueryRunner(QObject):
    queryStarted = Signal()  # For loading indicator
    queryDone = Signal()  # For loading indicator
    _queryResultAvailable = Signal()
    _readyForNewQuery = Signal()

    def __init__(self, wikibaseConfig: WikibaseConfig) -> None:
        super().__init__()

        self._wikibaseConfig = wikibaseConfig
        self._updatePrefixes()

        self._callbackConnection: Optional[QMetaObject.Connection] = None
        self._executingQuery = False
        self._queryQueue: list[tuple[str, Callable[[], None], object]] = []

        self.callbackData: Optional[object] = None
        self.mostRecentQuery = ""
        self.queryResult: Optional[Table[str]] = None

        self._connectSignals()

    def _connectSignals(self) -> None:
        self._wikibaseConfig.wikibaseConfigChanged.connect(self._queryQueue.clear)
        self._wikibaseConfig.wikibaseConfigChanged.connect(self._updatePrefixes)
        self._readyForNewQuery.connect(self._handleNextQueryInQueue)

    def _updatePrefixes(self) -> None:
        self.queryPrefixes = f"""
            PREFIX kp:<{ config[WbiConfigKey.WIKIBASE_URL] }/entity/>
            PREFIX kpt:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/direct/>
            PREFIX kpp:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/>
            PREFIX kpps:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/statement/>
            PREFIX kppq:<{ config[WbiConfigKey.WIKIBASE_URL] }/prop/qualifier/>
        """

    def queueQueryForExecution(
        self, queryString: str, callback: Callable[[], None], data: object = None
    ) -> None:
        self._queryQueue.append((queryString, callback, data))
        if len(self._queryQueue) == 1 and not self._executingQuery:
            self._handleNextQueryInQueue()

    def _handleNextQueryInQueue(self) -> None:
        if not self._queryQueue:
            return
        (queryString, callback, data) = self._queryQueue.pop(0)
        self._executeQueryOnThread(queryString, callback, data)

    def _executeQueryOnThread(
        self, queryString: str, callback: Callable[[], None], data: object
    ) -> None:
        if self._executingQuery:
            return
        else:
            self._executingQuery = True

        if self._callbackConnection:
            self._queryResultAvailable.disconnect(self._callbackConnection)

        self._callbackConnection = self._queryResultAvailable.connect(callback)

        self.callbackData = data

        self.queryThread = QueryThread(self, queryString, self.queryPrefixes)
        self.queryThread.resultReady.connect(self._onQueryThreadResultReady)
        self.queryThread.finished.connect(self.queryThread.deleteLater)
        self.queryThread.destroyed.connect(self._onQueryThreadDestroyed)

        self.mostRecentQuery = queryString
        self.queryStarted.emit()
        self.queryThread.start()

    def _onQueryThreadResultReady(self) -> None:
        self.queryResult = self.queryThread.resultTable
        self._queryResultAvailable.emit()
        self.queryDone.emit()

    def _onQueryThreadDestroyed(self) -> None:
        self._executingQuery = False
        self._readyForNewQuery.emit()
