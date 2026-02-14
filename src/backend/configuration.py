from enum import StrEnum
from itertools import chain
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


class ExtraWikibaseConfigKey(StrEnum):
    """
    Extra keys that configure a wikibase instance that are needed, but do not
    exaclty match a config key for the wikibaseintegrator package.
    """

    INSTANCE_OF_PID = "INSTANCE_OF_PID"
    SUBCLASS_OF_PID = "SUBCLASS_OF_PID"


CONFIG_KEY_TYPES = [WbiConfigKey, ExtraWikibaseConfigKey]


class Configuration(QObject):
    wbiConfigChanged = Signal()
    extraWikibaseConfigChanged = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._settings = QSettings(ORGANISATION_NAME, APPLICATION_NAME)
        self._keyTypeModified = {keyType: False for keyType in CONFIG_KEY_TYPES}

    def getWikibaseConfig(self) -> Mapping[str, str]:
        self._settings.beginGroup(WBI_CONFIGURATION_KEY)
        result = {
            key: self._settings.value(key)
            for key in self._settings.allKeys()
            if key in chain(*CONFIG_KEY_TYPES)  # type: ignore
        }
        self._settings.endGroup()
        return result

    def setWikibaseConfig(
        self, newSettings: Mapping[str, str | int | bool | None]
    ) -> None:

        self._settings.beginGroup(WBI_CONFIGURATION_KEY)
        for keyType in CONFIG_KEY_TYPES:
            self._setSettingsValuesForKeyType(newSettings, keyType)
        self._settings.endGroup()

        self._emitSignalsIfNeeded()

    def _setSettingsValuesForKeyType(
        self, newSettings: Mapping[str, str | int | bool | None], keyType: type[StrEnum]
    ) -> None:
        self._keyTypeModified[keyType] = False
        for key in keyType:
            value = newSettings.get(key)
            if value is not None:
                self._settings.setValue(key, value)
                self._keyTypeModified[keyType] = True

    def _emitSignalsIfNeeded(self) -> None:
        if self._keyTypeModified[WbiConfigKey]:
            self.wbiConfigChanged.emit()
        if self._keyTypeModified[ExtraWikibaseConfigKey]:
            self.extraWikibaseConfigChanged.emit()
