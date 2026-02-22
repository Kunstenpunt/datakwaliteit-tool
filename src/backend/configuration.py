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


ConfigMapping = Mapping[str, str | int | bool | None]


class ConfigHandler(QObject):
    configChanged = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._settings = QSettings(ORGANISATION_NAME, APPLICATION_NAME)
        self._modified = False

    def getWikibaseConfigPairs(self) -> ConfigMapping:
        self._settings.beginGroup(WBI_CONFIGURATION_KEY)
        configPairs = {
            key: self._settings.value(key)
            for key in self._settings.allKeys()
            if key in chain(*CONFIG_KEY_TYPES)  # type: ignore
        }
        self._settings.endGroup()
        return configPairs

    def setWikibaseConfigPairs(self, newConfigPairs: ConfigMapping) -> None:
        self._modified = False
        self._settings.beginGroup(WBI_CONFIGURATION_KEY)
        for keyType in CONFIG_KEY_TYPES:
            self._setSettingsValuesForKeyType(newConfigPairs, keyType)
        self._settings.endGroup()

        self._emitSignalIfNeeded()

    def _setSettingsValuesForKeyType(
        self,
        newConfigPairs: ConfigMapping,
        keyType: type[StrEnum],
    ) -> None:
        for key in keyType:
            if key in newConfigPairs:
                value = newConfigPairs[key]
                self._settings.setValue(key, value)
                self._modified = True

    def _emitSignalIfNeeded(self) -> None:
        if self._modified:
            self._modified = False
            self.configChanged.emit()
