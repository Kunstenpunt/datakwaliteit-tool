from enum import StrEnum

from PySide6.QtCore import QObject, QSettings

ORGANISATION_NAME = "Kunstenpunt"
APPLICATION_NAME = "datakwaliteit-tool"
WBI_CONFIGURATION_KEY = "wikibase"


class WbiConfigKey(StrEnum):
    """
    Keys that exactly match a config key for the wikibaseintegrator package.
    """
    DEFAULT_LANGUAGE = "DEFAULT_LANGUAGE"
    WIKIBASE_URL = "WIKIBASE_URL"
    MEDIAWIKI_API_URL = "MEDIAWIKI_API_URL"
    MEDIAWIKI_INDEX_URL = "MEDIAWIKI_INDEX_URL"
    MEDIAWIKI_REST_URL = "MEDIAWIKI_REST_URL"
    SPARQL_ENDPOINT_URL = "SPARQL_ENDPOINT_URL"
    PROPERTY_CONSTRAINT_PID = "PROPERTY_CONSTRAINT_PID"


class ExtraWikibaseKey(StrEnum):
    """
    Extra keys that configure a wikibase instance that are needed, but do not
    exaclty match a config key for the wikibaseintegrator package.
    """
    INSTANCE_OF_PID = "INSTANCE_OF_PID"
    SUBCLASS_OF_PID = "SUBCLASS_OF_PID"


class Configuration(QObject):
    def __init__(self):
        self.settings = QSettings(ORGANISATION_NAME, APPLICATION_NAME)

    def getWikibaseConfig(self):
        self.settings.beginGroup(WBI_CONFIGURATION_KEY)
        result = {
            key: self.settings.value(key)
            for key in self.settings.allKeys()
            if key in WbiConfigKey or key in ExtraWikibaseKey
        }
        self.settings.endGroup()
        return result

    def setWikibaseConfig(self, data):
        self.settings.beginGroup(WBI_CONFIGURATION_KEY)
        for keyList in WbiConfigKey, ExtraWikibaseKey:
            for key in keyList:
                value = data.get(key)
                if value is not None:
                    self.settings.setValue(key, value)
        self.settings.endGroup()
