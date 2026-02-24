from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_wikibaseConfig():
    wikibaseConfigMock = Mock()
    wikibaseConfigMock.getBaseUrl.return_value = "https://base.url"
    wikibaseConfigMock.getDefaultLanguage.return_value = "nl"
    wikibaseConfigMock.getInstanceOfPid = "P31"
    wikibaseConfigMock.getPropertyConstraintPid = "P2301"
    wikibaseConfigMock.getPureUrl = "base.url"
    wikibaseConfigMock.getSubclassOfPid = "P279"

    return wikibaseConfigMock


@pytest.fixture
def mock_wikibaseQueryRunner():
    wikibaseQueryRunnerMock = Mock()

    def mock_queueQueryForExecution(query, callback):
        callback()

    wikibaseQueryRunnerMock.queueQueryForExecution.side_effect = (
        mock_queueQueryForExecution
    )

    return wikibaseQueryRunnerMock
