import random
import sys
import uuid

from src.backend.configuration import ConfigHandler

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


def test_configHandler(qtbot):
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
