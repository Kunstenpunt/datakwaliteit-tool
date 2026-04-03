from time import sleep

from PySide6.QtCore import QObject, QThread, Signal


class ConfigHandlerStub(QObject):
    configChanged = Signal()

    configPairs = {}

    def __init__(self) -> None:
        super().__init__()

    def getWikibaseConfigPairs(self):
        return ConfigHandlerStub.configPairs

    def setWikibaseConfigPairs(self, newConfigPairs) -> None:
        if ConfigHandlerStub.configPairs != newConfigPairs:
            ConfigHandlerStub.configPairs = newConfigPairs.copy()
            self.configChanged.emit()


class QueryThreadStub(QThread):
    THREAD_EXECUTION_TIME_SECONDS = 0.01

    resultReady = Signal()

    predefinedResultTables = []
    predefinedResultIndex = 0
    latestQuery = ""
    latestDefaultPrefixes = ""

    def __init__(self, parent, query, defaultPrefixes) -> None:
        super().__init__(parent)
        QueryThreadStub.latestQuery = query
        QueryThreadStub.latestDefaultPrefixes = defaultPrefixes

    def run(self) -> None:
        sleep(self.THREAD_EXECUTION_TIME_SECONDS)
        self.resultTable = QueryThreadStub.predefinedResultTables[
            QueryThreadStub.predefinedResultIndex
        ]
        QueryThreadStub.predefinedResultIndex += 1
        self.resultReady.emit()


class WikibaseConfigStub(QObject):
    wikibaseConfigChanged = Signal()

    def __init__(self, configHandler=None) -> None:
        super().__init__()
        self.baseUrl = "https://base.url"
        self.defaultLanguage = "nl"
        self.instanceOfPid = "P31"
        self.propertyConstraintPid = "P2301"
        self.pureUrl = "base.url"
        self.subclassOfPid = "P279"


class WikibaseQueryRunnerStub(QObject):
    queryStarted = Signal()
    queryDone = Signal()

    def __init__(self, wikibaseConfig=None) -> None:
        super().__init__()
        self.queueQueryForExecutionCalls = []

        self.callbackData = None
        self.mostRecentQuery = ""
        self.queryResult = None

    def queueQueryForExecution(self, queryString, callback, data=None):
        self.queueQueryForExecutionCalls += (queryString, callback, data)

        self.callbackData = self.callbackData
        self.mostRecentQuery = queryString

        callback()
        self.queryDone.emit()
