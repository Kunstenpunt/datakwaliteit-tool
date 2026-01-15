from PySide6.QtWidgets import QWidget

from .designer.configurationtab import Ui_ConfigurationTab
from ..backend.configuration import ExtraWikibaseKey, WbiConfigKey


class ConfigurationTab(QWidget, Ui_ConfigurationTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model

        self.discardButton.clicked.connect(self.loadConfig)
        self.saveButton.clicked.connect(self.saveConfig)

        self.lineEdits = {
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

        for lineEdit, key in self.lineEdits.items():
            self.setupLineEdit(lineEdit, key)

        self.loadConfig()

    def setupLineEdit(self, lineEdit, key):
        lineEdit.textEdited.connect(self.onTextEdited(lineEdit, key))

    def onTextEdited(self, lineEdit, key):
        def callback(text):
            lineEdit.wbiValueModified = (
                text != self.model.configuration.getWikibaseConfig().get(key)
            )
            self.updateFontLineEdit(lineEdit)
            self.updateEnabledButtons()

        return callback

    def updateFontLineEdit(self, lineEdit):
        font = lineEdit.font()
        font.setBold(lineEdit.wbiValueModified and lineEdit.text() != "")
        lineEdit.setFont(font)

    def loadConfig(self):
        config = self.model.configuration.getWikibaseConfig()
        for lineEdit, key in self.lineEdits.items():
            lineEdit.setText(config.get(key))
            lineEdit.wbiValueModified = False
            self.updateFontLineEdit(lineEdit)
        self.updateEnabledButtons()

    def saveConfig(self):
        config = {}
        for lineEdit, key in self.lineEdits.items():
            config[key] = lineEdit.text()
        self.model.configuration.setWikibaseConfig(config)
        self.loadConfig()

    def updateEnabledButtons(self):
        for lineEdit in self.lineEdits.keys():
            if lineEdit.wbiValueModified:
                self.saveButton.setEnabled(True)
                self.discardButton.setEnabled(True)
                return
        self.saveButton.setEnabled(False)
        self.discardButton.setEnabled(False)
