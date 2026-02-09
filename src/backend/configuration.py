from enum import StrEnum
from typing import Mapping

from PySide6.QtCore import Signal, QObject, QSettings

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
    wbiConfigChanged = Signal()
    extraWikibaseConfigChanged = Signal()

    def __init__(self) -> None:
        super().__init__()

        self.settings = QSettings(ORGANISATION_NAME, APPLICATION_NAME)

    def getWikibaseConfig(self) -> Mapping[str, str]:
        self.settings.beginGroup(WBI_CONFIGURATION_KEY)
        result = {
            key: self.settings.value(key)
            for key in self.settings.allKeys()
            if key in WbiConfigKey or key in ExtraWikibaseKey
        }
        self.settings.endGroup()
        return result

    def setWikibaseConfig(self, data: Mapping[str, str | int | bool | None]) -> None:
        wbiModified = False
        extraModified = False

        self.settings.beginGroup(WBI_CONFIGURATION_KEY)
        for key in WbiConfigKey:
            value = data.get(key)
            if value is not None:
                self.settings.setValue(key, value)
                wbiModified = True

        for keyExtra in ExtraWikibaseKey:
            value = data.get(keyExtra)
            if value is not None:
                self.settings.setValue(keyExtra, value)
                extraModified = True

        self.settings.endGroup()

        if wbiModified:
            self.wbiConfigChanged.emit()
        if extraModified:
            self.extraWikibaseConfigChanged.emit()
