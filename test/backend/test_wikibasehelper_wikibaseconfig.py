import pytest

from src.backend.wikibasehelper import config, WbiConfigKey, WikibaseConfig
from test.backend.stubs import ConfigHandlerStub

INITIAL_CONFIG_PAIRS = {
    "DEFAULT_LANGUAGE": "nl",
    "WIKIBASE_URL": "https://base.url",
    "MEDIAWIKI_API_URL": "https://base.url/w/api.php",
    "MEDIAWIKI_INDEX_URL": "https://base.url/w/index.php",
    "MEDIAWIKI_REST_URL": "https://base.url/w/rest.php",
    "SPARQL_ENDPOINT_URL": "https://base.url/sparql",
    "PROPERTY_CONSTRAINT_PID": "P2301",
    "INSTANCE_OF_PID": "P31",
    "SUBCLASS_OF_PID": "P279",
}

MODIFIED_CONFIG_PAIRS = {
    "DEFAULT_LANGUAGE": "en",
    "WIKIBASE_URL": "https://other.url",
    "MEDIAWIKI_API_URL": "https://other.url/w/api.php",
    "MEDIAWIKI_INDEX_URL": "https://other.url/w/index.php",
    "MEDIAWIKI_REST_URL": "https://other.url/w/rest.php",
    "SPARQL_ENDPOINT_URL": "https://other.url/sparql",
    "PROPERTY_CONSTRAINT_PID": "P42",
    "INSTANCE_OF_PID": "P43",
    "SUBCLASS_OF_PID": "P44",
}

STRANGE_CONFIG_PAIRS = {
    "DEFAULT_LANGUAGE": 1,
    "WIKIBASE_URL": False,
    "MEDIAWIKI_API_URL": None,
    "MEDIAWIKI_INDEX_URL": True,
    "MEDIAWIKI_REST_URL": 3,
    "SPARQL_ENDPOINT_URL": False,
    "PROPERTY_CONSTRAINT_PID": 4,
    "INSTANCE_OF_PID": [False, True],
    "SUBCLASS_OF_PID": None,
}

INCOMPLETE_CONFIG_PAIRS = {
    "DEFAULT_LANGUAGE": "nl",
    "INSTANCE_OF_PID": "P31",
    "SUBCLASS_OF_PID": "P279",
}


@pytest.fixture
def configBackup():
    backupConfig = getWbiConfig()
    yield
    config.update(backupConfig)


def getWbiConfig():
    return {key: config[key] for key in WbiConfigKey}


def checkWbiConfig(expectedConfigPairs):
    for key in WbiConfigKey:
        assert config[key] == expectedConfigPairs[key]


def test_WikibaseConfigStandard(configBackup, qtbot):
    ConfigHandlerStub.configPairs = INITIAL_CONFIG_PAIRS.copy()
    configHandlerStub = ConfigHandlerStub()

    wikibaseConfig = WikibaseConfig(configHandlerStub)
    checkWbiConfig(INITIAL_CONFIG_PAIRS)
    assert wikibaseConfig.propertyConstraintPid == "P2301"
    assert wikibaseConfig.defaultLanguage == "nl"
    assert wikibaseConfig.baseUrl == "https://base.url"
    assert wikibaseConfig.pureUrl == "base.url"
    assert wikibaseConfig.instanceOfPid == "P31"
    assert wikibaseConfig.subclassOfPid == "P279"

    with qtbot.waitSignal(wikibaseConfig.wikibaseConfigChanged):
        configHandlerStub.setWikibaseConfigPairs(MODIFIED_CONFIG_PAIRS)

    checkWbiConfig(MODIFIED_CONFIG_PAIRS)
    assert wikibaseConfig.propertyConstraintPid == "P42"
    assert wikibaseConfig.defaultLanguage == "en"
    assert wikibaseConfig.baseUrl == "https://other.url"
    assert wikibaseConfig.pureUrl == "other.url"
    assert wikibaseConfig.instanceOfPid == "P43"
    assert wikibaseConfig.subclassOfPid == "P44"

    with qtbot.waitSignal(wikibaseConfig.wikibaseConfigChanged):
        configHandlerStub.setWikibaseConfigPairs(STRANGE_CONFIG_PAIRS)

    checkWbiConfig(STRANGE_CONFIG_PAIRS)
    assert wikibaseConfig.propertyConstraintPid == ""
    assert wikibaseConfig.defaultLanguage == ""
    assert wikibaseConfig.baseUrl == ""
    assert wikibaseConfig.pureUrl == ""
    assert wikibaseConfig.instanceOfPid == ""
    assert wikibaseConfig.subclassOfPid == ""


def test_WikibaseConfigIncomplete(configBackup, qtbot):
    ConfigHandlerStub.configPairs = INCOMPLETE_CONFIG_PAIRS.copy()
    configHandlerStub = ConfigHandlerStub()

    configPairs = getWbiConfig()
    configPairs.update(INCOMPLETE_CONFIG_PAIRS)

    wikibaseConfig = WikibaseConfig(configHandlerStub)
    checkWbiConfig(configPairs)
    assert (
        wikibaseConfig.propertyConstraintPid
        == config[WbiConfigKey.PROPERTY_CONSTRAINT_PID]
    )
    assert wikibaseConfig.defaultLanguage == configPairs[WbiConfigKey.DEFAULT_LANGUAGE]
    assert wikibaseConfig.baseUrl == configPairs[WbiConfigKey.WIKIBASE_URL]
    assert wikibaseConfig.instanceOfPid == ""
    assert wikibaseConfig.subclassOfPid == ""
