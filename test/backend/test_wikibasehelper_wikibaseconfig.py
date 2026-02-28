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
    ConfigHandlerStub.configPairs = INITIAL_CONFIG_PAIRS[:]
    configHandlerStub = ConfigHandlerStub()

    wikibaseConfig = WikibaseConfig(configHandlerStub)
    checkWbiConfig(INITIAL_CONFIG_PAIRS)
    assert wikibaseConfig.getPropertyConstraintPid() == "P2301"
    assert wikibaseConfig.getDefaultLanguage() == "nl"
    assert wikibaseConfig.getBaseUrl() == "https://base.url"
    assert wikibaseConfig.getPureUrl() == "base.url"
    assert wikibaseConfig.getInstanceOfPid() == "P31"
    assert wikibaseConfig.getSubclassOfPid() == "P279"

    with qtbot.waitSignal(wikibaseConfig.wikibaseConfigChanged):
        configHandlerStub.setWikibaseConfigPairs(MODIFIED_CONFIG_PAIRS)

    checkWbiConfig(MODIFIED_CONFIG_PAIRS)
    assert wikibaseConfig.getPropertyConstraintPid() == "P42"
    assert wikibaseConfig.getDefaultLanguage() == "en"
    assert wikibaseConfig.getBaseUrl() == "https://other.url"
    assert wikibaseConfig.getPureUrl() == "other.url"
    assert wikibaseConfig.getInstanceOfPid() == "P43"
    assert wikibaseConfig.getSubclassOfPid() == "P44"

    with qtbot.waitSignal(wikibaseConfig.wikibaseConfigChanged):
        configHandlerStub.setWikibaseConfigPairs(STRANGE_CONFIG_PAIRS)

    checkWbiConfig(STRANGE_CONFIG_PAIRS)
    assert wikibaseConfig.getPropertyConstraintPid() == ""
    assert wikibaseConfig.getDefaultLanguage() == ""
    assert wikibaseConfig.getBaseUrl() == ""
    assert wikibaseConfig.getPureUrl() == ""
    assert wikibaseConfig.getInstanceOfPid() == ""
    assert wikibaseConfig.getSubclassOfPid() == ""


def test_WikibaseConfigIncomplete(configBackup, qtbot):
    ConfigHandlerStub.configPairs = INCOMPLETE_CONFIG_PAIRS[:]
    configHandlerStub = ConfigHandlerStub()

    configPairs = getWbiConfig()
    configPairs.update(INCOMPLETE_CONFIG_PAIRS)

    wikibaseConfig = WikibaseConfig(configHandlerStub)
    checkWbiConfig(configPairs)
    assert (
        wikibaseConfig.getPropertyConstraintPid()
        == config[WbiConfigKey.PROPERTY_CONSTRAINT_PID]
    )
    assert (
        wikibaseConfig.getDefaultLanguage()
        == configPairs[WbiConfigKey.DEFAULT_LANGUAGE]
    )
    assert wikibaseConfig.getBaseUrl() == configPairs[WbiConfigKey.WIKIBASE_URL]
    assert wikibaseConfig.getInstanceOfPid() == ""
    assert wikibaseConfig.getSubclassOfPid() == ""
