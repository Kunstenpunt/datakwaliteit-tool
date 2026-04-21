from typing import Callable

from PySide6.QtWidgets import QLineEdit, QWidget

from ..backend.configuration import (
    ExtraWikibaseConfigKey,
    SensitiveConfigKey,
    WbiConfigKey,
)
from ..backend.model import Model
from ..backend.utils import stringOrDefault

from .designer.configurationtab import Ui_ConfigurationTab


class ConfigurationTab(QWidget, Ui_ConfigurationTab):
    def __init__(self, model: Model) -> None:
        super().__init__()
        self.setupUi(self)  # type: ignore

        self._model = model

        self.discardButton.clicked.connect(self._loadConfig)
        self.saveButton.clicked.connect(self._saveConfig)
        self.botPasswordHideToggle.clicked.connect(self._toggleBotPasswordReadable)
        self.botPasswordRemoveButton.clicked.connect(self._removeBotPassword)

        self._lineEditsToConfigKeys = {
            self.wikibaseUrlLineEdit: WbiConfigKey.WIKIBASE_URL,
            self.defaultLanguageLineEdit: WbiConfigKey.DEFAULT_LANGUAGE,
            self.mediawikiApiUrlLineEdit: WbiConfigKey.MEDIAWIKI_API_URL,
            self.mediawikiIndexUrlLineEdit: WbiConfigKey.MEDIAWIKI_INDEX_URL,
            self.mediawikiRestUrlLineEdit: WbiConfigKey.MEDIAWIKI_REST_URL,
            self.sparqlEndpointUrlLineEdit: WbiConfigKey.SPARQL_ENDPOINT_URL,
            self.propertyConstraintPidLineEdit: WbiConfigKey.PROPERTY_CONSTRAINT_PID,
            self.exceptionToConstraintPidLineEdit: ExtraWikibaseConfigKey.EXCEPTION_TO_CONSTRAINT_PID,
            self.instanceOfPidLineEdit: ExtraWikibaseConfigKey.INSTANCE_OF_PID,
            self.subclassOfPidLineEdit: ExtraWikibaseConfigKey.SUBCLASS_OF_PID,
            self.botUsernameLineEdit: ExtraWikibaseConfigKey.BOT_USERNAME,
            self.botPasswordLineEdit: SensitiveConfigKey.BOT_PASSWORD,
        }

        self._lineEditsWbiValueModified = {
            x: False for x in self._lineEditsToConfigKeys.keys()
        }

        for lineEdit, key in self._lineEditsToConfigKeys.items():
            self._setupLineEdit(lineEdit, key)

        self._loadConfig()

    def _setupLineEdit(self, lineEdit: QLineEdit, key: str) -> None:
        lineEdit.textEdited.connect(self._createTextEditedCallback(lineEdit, key))

    def _createTextEditedCallback(
        self, lineEdit: QLineEdit, key: str
    ) -> Callable[[str], None]:
        def onTextEdited(text: str) -> None:
            self._lineEditsWbiValueModified[lineEdit] = (
                text != self._model.configHandler.getSingleValue(key)
            )
            self._updateLineEditFont(lineEdit)
            self._updateEnabledButtons()

        return onTextEdited

    def _updateLineEditFont(self, lineEdit: QLineEdit) -> None:
        font = lineEdit.font()
        font.setBold(
            self._lineEditsWbiValueModified[lineEdit] and lineEdit.text() != ""
        )
        lineEdit.setFont(font)

    def _cleanUpLineEditText(self, lineEdit: QLineEdit) -> None:
        text = lineEdit.text().strip()

        # Strip trailing "/" for correct wbi_config parameters
        if lineEdit in [
            self.wikibaseUrlLineEdit,
            self.mediawikiApiUrlLineEdit,
            self.mediawikiIndexUrlLineEdit,
            self.mediawikiRestUrlLineEdit,
            self.sparqlEndpointUrlLineEdit,
        ]:
            text = text.rstrip("/")

        lineEdit.setText(text)

    def _loadConfig(self) -> None:
        config = self._model.configHandler.getWikibaseConfigPairs()
        for lineEdit, key in self._lineEditsToConfigKeys.items():
            lineEdit.setText(stringOrDefault(config.get(key)))
            self._lineEditsWbiValueModified[lineEdit] = False
            self._updateLineEditFont(lineEdit)
        self._updateEnabledButtons()

    def _saveConfig(self) -> None:
        config: dict[str, str] = {}
        for lineEdit, key in self._lineEditsToConfigKeys.items():
            if self._lineEditsWbiValueModified[lineEdit]:
                self._cleanUpLineEditText(lineEdit)
                config[key] = lineEdit.text()
        self._model.configHandler.setWikibaseConfigPairs(config)
        self._loadConfig()

    def _updateEnabledButtons(self) -> None:
        for lineEdit in self._lineEditsToConfigKeys.keys():
            if self._lineEditsWbiValueModified[lineEdit]:
                self.saveButton.setEnabled(True)
                self.discardButton.setEnabled(True)
                return
        self.saveButton.setEnabled(False)
        self.discardButton.setEnabled(False)

    def _toggleBotPasswordReadable(self) -> None:
        self.botPasswordLineEdit.setEchoMode(
            QLineEdit.EchoMode.Password
            if self.botPasswordLineEdit.echoMode() == QLineEdit.EchoMode.Normal
            else QLineEdit.EchoMode.Normal
        )

    def _removeBotPassword(self) -> None:
        self._model.configHandler.removeSensitiveKey(
            self.botUsernameLineEdit.text().strip(), ExtraWikibaseConfigKey.BOT_USERNAME
        )
        self.botPasswordLineEdit.setText("")
