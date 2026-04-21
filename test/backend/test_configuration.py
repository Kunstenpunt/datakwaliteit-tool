import random
import sys
import uuid

import pytest

from PySide6.QtCore import QSettings

from src.datakwaliteit_tool.backend.configuration import ConfigHandler
from src.datakwaliteit_tool.backend.configuration import (
    ORGANISATION_NAME,
    APPLICATION_NAME,
    WBI_CONFIGURATION_KEY,
)

validWbiConfigKeys = [
    "DEFAULT_LANGUAGE",
    "WIKIBASE_URL",
    "MEDIAWIKI_API_URL",
    "MEDIAWIKI_INDEX_URL",
    "MEDIAWIKI_REST_URL",
    "SPARQL_ENDPOINT_URL",
    "PROPERTY_CONSTRAINT_PID",
]

validExtraWikibaseConfigKeys = [
    "SUBCLASS_OF_PID",
    "INSTANCE_OF_PID",
]

invalidKey = "UNKNOWN KEY"


@pytest.fixture
def configBackup():
    qSettings = QSettings(ORGANISATION_NAME, APPLICATION_NAME)
    qSettings.beginGroup(WBI_CONFIGURATION_KEY)
    configPairs = {k: qSettings.value(k) for k in qSettings.allKeys()}
    qSettings.endGroup()
    yield
    qSettings.beginGroup(WBI_CONFIGURATION_KEY)
    for k, v in configPairs.items():
        qSettings.setValue(k, v)
    qSettings.endGroup()


def test_configHandler(configBackup, qtbot):
    configHandler = ConfigHandler()

    newKeys = validWbiConfigKeys + validExtraWikibaseConfigKeys + [invalidKey]

    newConfig = generateConfigForKeys(newKeys)
    validConfig = {k: v for k, v in newConfig.items() if k != invalidKey}

    with qtbot.waitSignal(
        configHandler.configChanged,
        raising=True,
        check_params_cb=createCallbackCheckConfiguration(validConfig),
    ):
        configHandler.setWikibaseConfigPairs(newConfig)

    assert not invalidKey in configHandler.getWikibaseConfigPairs()

    with qtbot.assertNotEmitted(configHandler.configChanged):
        configHandler.setWikibaseConfigPairs({invalidKey: "x"})


def generateConfigForKeys(keys):
    randomOffset = random.randrange(4)

    return {
        key: [
            str(uuid.uuid4()),
            random.choice([True, False]),
            random.randrange(sys.maxsize),
            None,
        ][(i + randomOffset) % 4]
        for i, key in enumerate(keys)
    }


def createCallbackCheckConfiguration(validConfig):
    def checkConfiguration():
        config = ConfigHandler().getWikibaseConfigPairs()
        mismatchedKeys = [
            valdidKey
            for valdidKey, validItem in validConfig.items()
            if config.get(valdidKey) != validItem
        ]
        return len(mismatchedKeys) == 0

    return checkConfiguration
