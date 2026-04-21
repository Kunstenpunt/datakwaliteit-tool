from itertools import product
from unittest.mock import patch

from PySide6.QtCore import QObject

from src.backend.wikibasehelper import QueryThread

correctMockReturn = {
    "head": {"vars": ["x"]},
    "results": {"bindings": [{"x": {"value": "1"}}]},
}
correctResultTable = [["x"], ["1"]]

queryWithPrefix = "# comment\n   PREFIX included prefix\nquery"
queryNoPrefix = "query"
defaultPrefix = "PREFIX default prefix"


def run_queryThread(queryThread, qtbot, expectedResult):
    def check_resultTable():
        return queryThread.resultTable == expectedResult

    with qtbot.waitSignal(
        queryThread.resultReady,
        raising=True,
        check_params_cb=check_resultTable,
    ):
        queryThread.run()


def test_withPrefixNoResult(qtbot, subtests):
    for mockReturnValue, mockSideEffect in product(
        [None, "wrong type"], [None, Exception()]
    ):
        with (
            subtests.test(
                mockReturnValue=mockReturnValue, mockSideEffect=mockSideEffect
            ),
            patch("src.backend.wikibasehelper.execute_sparql_query") as mock,
        ):
            parent = QObject()
            mock.reset_mock()
            mock.return_value = mockReturnValue
            mock.side_effect = mockSideEffect

            queryThread = QueryThread(
                parent,
                queryWithPrefix,
                defaultPrefix,
            )
            queryThread.resultTable = "old_result"

            run_queryThread(queryThread, qtbot, None)

            mock.assert_called_once()
            mockArgs = mock.call_args.args
            assert mockArgs[0] == queryWithPrefix
            assert mockArgs[1] == None


def test_noPrefixNoResult(qtbot, subtests):
    for mockReturnValue, mockSideEffect in product(
        [None, "wrong type"], [None, Exception()]
    ):
        with (
            subtests.test(
                mockReturnValue=mockReturnValue, mockSideEffect=mockSideEffect
            ),
            patch("src.backend.wikibasehelper.execute_sparql_query") as mock,
        ):
            parent = QObject()
            mock.return_value = mockReturnValue
            mock.side_effect = mockSideEffect

            queryThread = QueryThread(
                parent,
                queryNoPrefix,
                defaultPrefix,
            )
            queryThread.resultTable = "old_result"

            run_queryThread(queryThread, qtbot, None)

            mock.assert_called_once()
            mockArgs = mock.call_args.args
            assert mockArgs[0] == queryNoPrefix
            assert mockArgs[1] == defaultPrefix


def test_withPrefixCorrectResult(qtbot):
    with patch("src.backend.wikibasehelper.execute_sparql_query") as mock:
        parent = QObject()
        mock.return_value = correctMockReturn

        queryThread = QueryThread(
            parent,
            queryWithPrefix,
            defaultPrefix,
        )
        queryThread.resultTable = "old_result"

        run_queryThread(queryThread, qtbot, correctResultTable)

        mock.assert_called_once()
        mockArgs = mock.call_args.args
        assert mockArgs[0] == queryWithPrefix
        assert mockArgs[1] == None


def test_noPrefixCorrectResult(qtbot):
    with patch("src.backend.wikibasehelper.execute_sparql_query") as mock:
        parent = QObject()
        mock.return_value = correctMockReturn

        queryThread = QueryThread(
            parent,
            queryNoPrefix,
            defaultPrefix,
        )
        queryThread.resultTable = "old_result"

        run_queryThread(queryThread, qtbot, correctResultTable)

        mock.assert_called_once()
        mockArgs = mock.call_args.args
        assert mockArgs[0] == queryNoPrefix
        assert mockArgs[1] == defaultPrefix
