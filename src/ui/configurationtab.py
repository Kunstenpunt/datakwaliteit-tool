from typing import Callable

from PySide6.QtWidgets import QLineEdit, QWidget

from ..backend.configuration import ExtraWikibaseConfigKey, WbiConfigKey
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

        self._lineEditsToConfigKeys = {
            self.wikibaseUrlLineEdit: WbiConfigKey.WIKIBASE_URL,
            self.defaultLanguageLineEdit: WbiConfigKey.DEFAULT_LANGUAGE,
            self.mediawikiApiUrlLineEdit: WbiConfigKey.MEDIAWIKI_API_URL,
            self.mediawikiIndexUrlLineEdit: WbiConfigKey.MEDIAWIKI_INDEX_URL,
            self.mediawikiRestUrlLineEdit: WbiConfigKey.MEDIAWIKI_REST_URL,
            self.sparqlEndpointUrlLineEdit: WbiConfigKey.SPARQL_ENDPOINT_URL,
            self.propertyConstraintPidLineEdit: WbiConfigKey.PROPERTY_CONSTRAINT_PID,
            self.instanceOfPidLineEdit: ExtraWikibaseConfigKey.INSTANCE_OF_PID,
            self.subclassOfPidLineEdit: ExtraWikibaseConfigKey.SUBCLASS_OF_PID,
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
                text != self._model.configHandler.getWikibaseConfigPairs().get(key)
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
