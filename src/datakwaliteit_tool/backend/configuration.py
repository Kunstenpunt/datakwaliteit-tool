from enum import StrEnum
from itertools import chain
from typing import Any, Mapping

from PySide6.QtCore import Signal, QObject, QSettings

from keyring import delete_password, get_password, set_password

from .utils import stringOrDefault

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
    EXCEPTION_TO_CONSTRAINT_PID = "EXCEPTION_TO_CONSTRAINT_PID"
    BOT_USERNAME = "BOT_USERNAME"


class SensitiveConfigKey(StrEnum):
    """
    Extra keys for values that are sensitive and are not stored in plaintext.
    """

    BOT_PASSWORD = "BOT_PASSWORD"


CONFIG_KEY_TYPES = [WbiConfigKey, ExtraWikibaseConfigKey]


ConfigMapping = Mapping[str, str | int | bool | None]


class ConfigHandler(QObject):
    configChanged = Signal()

    def __init__(self) -> None:
        super().__init__()

        self._settings = QSettings(ORGANISATION_NAME, APPLICATION_NAME)
        self._modified = False

    def removeSensitiveKey(
        self, currentUsername: str, usernameKey: ExtraWikibaseConfigKey
    ) -> None:
        savedUsername = self.getSingleValue(usernameKey)
        try:
            delete_password(APPLICATION_NAME, savedUsername)
            delete_password(APPLICATION_NAME, currentUsername)
        except:
            pass
        self.configChanged.emit()

    def getSingleValue(self, key: str) -> Any:
        self._settings.beginGroup(WBI_CONFIGURATION_KEY)
        value = self._settings.value(key)
        self._settings.endGroup()
        return value

    def getWikibaseConfigPairs(self) -> ConfigMapping:
        self._settings.beginGroup(WBI_CONFIGURATION_KEY)
        configPairs = {
            key: self._settings.value(key)
            for key in self._settings.allKeys()
            if key in chain(*CONFIG_KEY_TYPES)  # type: ignore
        }
        self._settings.endGroup()

        botUsername = self.getSingleValue(ExtraWikibaseConfigKey.BOT_USERNAME)
        if botUsername:
            botPassword = get_password(APPLICATION_NAME, botUsername)
            if botPassword:
                configPairs[SensitiveConfigKey.BOT_PASSWORD] = botPassword

        return configPairs

    def setWikibaseConfigPairs(self, newConfigPairs: ConfigMapping) -> None:
        self._modified = False
        self._settings.beginGroup(WBI_CONFIGURATION_KEY)
        for keyType in CONFIG_KEY_TYPES:
            self._setSettingsValuesForKeyType(newConfigPairs, keyType)
        self._settings.endGroup()

        botUsername = self.getSingleValue(ExtraWikibaseConfigKey.BOT_USERNAME)
        botPassword = stringOrDefault(
            newConfigPairs.get(SensitiveConfigKey.BOT_PASSWORD)
        )
        if botUsername and botPassword:
            set_password(APPLICATION_NAME, botUsername, botPassword)
            self._modified = True

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
