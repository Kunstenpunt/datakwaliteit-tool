from time import sleep
from unittest.mock import patch

from PySide6.QtCore import QObject

from src.backend.wikibasehelper import WikibaseQueryRunner
from test.backend.stubs import QueryThreadStub, WikibaseConfigStub


queries = ["query 1", "query 2", "query 3", "query 4", "query 5"]
resultTables = [[["a"]], [["b"]], [["c"]], None, [["d"]]]
callbackData = [1, 2, 3, 4, 5]


class CallbackChecker:
    def __init__(self, wikibaseQueryRunner):
        self.callbacksCalled = 0
        self.wikibaseQueryRunner = wikibaseQueryRunner

    def generateNumberedCallback(self, index):
        def callback():
            assert self.callbacksCalled == index
            assert self.wikibaseQueryRunner.queryResult == resultTables[index]
            assert self.wikibaseQueryRunner.callbackData == callbackData[index]
            self.callbacksCalled = self.callbacksCalled + 1

        return callback


def test_WikibaseQueryRunner(qtbot):
    wikibaseConfigStub = WikibaseConfigStub()
    QueryThreadStub.predefinedResultTables = resultTables

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
            sleep(2)
            wikibaseQueryRunner.queueQueryForExecution(
                queries[-1],
                callbackChecker.generateNumberedCallback(len(queries) - 1),
                callbackData[len(queries) - 1],
            )
