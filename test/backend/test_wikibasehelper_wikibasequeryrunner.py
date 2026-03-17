from time import sleep
from unittest.mock import patch

from src.backend.wikibasehelper import (
    config,
    WbiConfigKey,
    WikibaseQueryRunner,
)
from test.backend.stubs import QueryThreadStub, WikibaseConfigStub

queries = ["query 1", "query 2", "query 3", "query 4", "query 5"]
resultTables = [[["a"], ["aa"], ["aaa"]], [["b"]], [["c"]], None, [["d"]]]
callbackData = [1, 2, None, "hello", 5]


class CallbackChecker:
    def __init__(self, wikibaseQueryRunner):
        self.callbacksCalled = 0
        self.wikibaseQueryRunner = wikibaseQueryRunner

    def _assertCallbackIndex(self, index):
        assert self.callbacksCalled == index

    def _assertCallbackAttributes(
        self,
        expectedQueryResult,
        expectedCallbackData,
        expectedQuery,
        expectedWikibaseUrl,
    ):
        assert self.wikibaseQueryRunner.queryResult == expectedQueryResult
        assert self.wikibaseQueryRunner.callbackData == expectedCallbackData
        assert self.wikibaseQueryRunner.mostRecentQuery == expectedQuery
        assert QueryThreadStub.latestQuery == expectedQuery
        assert QueryThreadStub.latestDefaultPrefixes == f"""
            PREFIX kp:<{expectedWikibaseUrl}/entity/>
            PREFIX kpt:<{expectedWikibaseUrl}/prop/direct/>
            PREFIX kpp:<{expectedWikibaseUrl}/prop/>
            PREFIX kpps:<{expectedWikibaseUrl}/prop/statement/>
            PREFIX kppq:<{expectedWikibaseUrl}/prop/qualifier/>
        """

    def generateCallback(
        self,
        expectedQueryResult,
        expectedCallbackData,
        expectedQuery,
        expectedWikibaseUrl,
    ):
        def callback():
            self._assertCallbackAttributes(
                expectedQueryResult,
                expectedCallbackData,
                expectedQuery,
                expectedWikibaseUrl,
            )

        return callback

    def generateNumberedCallback(self, index):
        def callback():
            self._assertCallbackIndex(index)
            self._assertCallbackAttributes(
                resultTables[index],
                callbackData[index],
                queries[index],
                config[WbiConfigKey.WIKIBASE_URL],
            )
            self.callbacksCalled = self.callbacksCalled + 1

        return callback


def test_WikibaseQueryRunnerStandard(qtbot):
    wikibaseConfigStub = WikibaseConfigStub()
    QueryThreadStub.predefinedResultTables = resultTables
    QueryThreadStub.predefinedResultIndex = 0

    with patch("src.backend.wikibasehelper.QueryThread", QueryThreadStub):
        wikibaseQueryRunner = WikibaseQueryRunner(wikibaseConfigStub)
        callbackChecker = CallbackChecker(wikibaseQueryRunner)

        with qtbot.waitSignals(
            [wikibaseQueryRunner.queryStarted, wikibaseQueryRunner.queryDone] * 5,
            order="strict",
            raising=True,
        ):
            for index, query in enumerate(queries[:-1]):
                wikibaseQueryRunner.queueQueryForExecution(
                    query,
                    callbackChecker.generateNumberedCallback(index),
                    callbackData[index],
                )
            # Test last one after queue should have fully emptied again
            sleep(QueryThreadStub.THREAD_EXECUTION_TIME_SECONDS * 10)
            wikibaseQueryRunner.queueQueryForExecution(
                queries[-1],
                callbackChecker.generateNumberedCallback(len(queries) - 1),
                callbackData[len(queries) - 1],
            )


def test_WikibaseQueryRunnerConfigChange(qtbot):
    # In this test, all but the last query are added.
    # Then the config is changed.
    # This should clear the queue.
    # Then the last query is added.
    # Only the first and final query should actually be executed if the test runs correctly.
    # The last query should have an updated default prefix.
    wikibaseConfigStub = WikibaseConfigStub()
    QueryThreadStub.predefinedResultTables = [
        resultTables[0],
        resultTables[-1],
    ]
    QueryThreadStub.predefinedResultIndex = 0

    with patch("src.backend.wikibasehelper.QueryThread", QueryThreadStub):
        wikibaseQueryRunner = WikibaseQueryRunner(wikibaseConfigStub)
        callbackChecker = CallbackChecker(wikibaseQueryRunner)

        with qtbot.waitSignals(
            [wikibaseQueryRunner.queryStarted, wikibaseQueryRunner.queryDone] * 2,
            order="strict",
            raising=True,
        ):
            for index, query in enumerate(queries[:-1]):
                wikibaseQueryRunner.queueQueryForExecution(
                    query,
                    lambda: None,
                    callbackData[index],
                )

            config[WbiConfigKey.WIKIBASE_URL] = "https://another.url"
            wikibaseConfigStub.wikibaseConfigChanged.emit()

            wikibaseQueryRunner.queueQueryForExecution(
                queries[-1],
                callbackChecker.generateCallback(
                    resultTables[-1],
                    callbackData[-1],
                    queries[-1],
                    "https://another.url",
                ),
                callbackData[-1],
            )
