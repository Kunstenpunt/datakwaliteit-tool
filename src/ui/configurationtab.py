from typing import Callable

from PySide6.QtWidgets import QLineEdit, QWidget

from ..backend.configuration import ExtraWikibaseKey, WbiConfigKey
from ..backend.model import Model

from .designer.configurationtab import Ui_ConfigurationTab


class ConfigurationTab(QWidget, Ui_ConfigurationTab):
    def __init__(self, model: Model) -> None:
        super().__init__()
        self.setupUi(self)  # type: ignore

        self.model = model

        self.discardButton.clicked.connect(self.loadConfig)
        self.saveButton.clicked.connect(self.saveConfig)

        self.lineEditsToConfigKeys = {
            self.wikibaseUrlLineEdit: WbiConfigKey.WIKIBASE_URL,
            self.defaultLanguageLineEdit: WbiConfigKey.DEFAULT_LANGUAGE,
            self.mediawikiApiUrlLineEdit: WbiConfigKey.MEDIAWIKI_API_URL,
            self.mediawikiIndexUrlLineEdit: WbiConfigKey.MEDIAWIKI_INDEX_URL,
            self.mediawikiRestUrlLineEdit: WbiConfigKey.MEDIAWIKI_REST_URL,
            self.sparqlEndpointUrlLineEdit: WbiConfigKey.SPARQL_ENDPOINT_URL,
            self.propertyConstraintPidLineEdit: WbiConfigKey.PROPERTY_CONSTRAINT_PID,
            self.instanceOfPidLineEdit: ExtraWikibaseKey.INSTANCE_OF_PID,
            self.subclassOfPidLineEdit: ExtraWikibaseKey.SUBCLASS_OF_PID,
        }

        self.lineEditsWbiValueModified = {
            x: False for x in self.lineEditsToConfigKeys.keys()
        }

        for lineEdit, key in self.lineEditsToConfigKeys.items():
            self.setupLineEdit(lineEdit, key)

        self.loadConfig()

    def setupLineEdit(self, lineEdit: QLineEdit, key: str) -> None:
        lineEdit.textEdited.connect(self.onTextEdited(lineEdit, key))

    def onTextEdited(self, lineEdit: QLineEdit, key: str) -> Callable[[str], None]:
        def callback(text: str) -> None:
            self.lineEditsWbiValueModified[lineEdit] = (
                text != self.model.configuration.getWikibaseConfig().get(key)
            )
            self.updateFontLineEdit(lineEdit)
            self.updateEnabledButtons()

        return callback

    def updateFontLineEdit(self, lineEdit: QLineEdit) -> None:
        font = lineEdit.font()
        font.setBold(self.lineEditsWbiValueModified[lineEdit] and lineEdit.text() != "")
        lineEdit.setFont(font)

    def cleanUpLineEditText(self, lineEdit: QLineEdit) -> None:
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

    def loadConfig(self) -> None:
        config = self.model.configuration.getWikibaseConfig()
        for lineEdit, key in self.lineEditsToConfigKeys.items():
            lineEdit.setText(config.get(key))
            self.lineEditsWbiValueModified[lineEdit] = False
            self.updateFontLineEdit(lineEdit)
        self.updateEnabledButtons()

    def saveConfig(self) -> None:
        config: dict[str, str] = {}
        for lineEdit, key in self.lineEditsToConfigKeys.items():
            if self.lineEditsWbiValueModified[lineEdit]:
                self.cleanUpLineEditText(lineEdit)
                config[key] = lineEdit.text()
        self.model.configuration.setWikibaseConfig(config)
        self.loadConfig()

    def updateEnabledButtons(self) -> None:
        for lineEdit in self.lineEditsToConfigKeys.keys():
            if self.lineEditsWbiValueModified[lineEdit]:
                self.saveButton.setEnabled(True)
                self.discardButton.setEnabled(True)
                return
        self.saveButton.setEnabled(False)
        self.discardButton.setEnabled(False)
