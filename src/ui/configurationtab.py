from PySide6.QtWidgets import QWidget

from .designer.configurationtab import Ui_ConfigurationTab
from ..backend.configuration import ExtraWikibaseKey, WbiConfigKey


class ConfigurationTab(QWidget, Ui_ConfigurationTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model

        self.saveButton.clicked.connect(self.saveConfig)

    def loadConfig(self):
        config = self.model.configuration.getWikibaseConfig()
        self.wikibaseUrlLineEdit.setText(config.get(WbiConfigKey.WIKIBASE_URL))
        self.defaultLanguageLineEdit.setText(config.get(WbiConfigKey.DEFAULT_LANGUAGE))
        self.mediawikiApiUrlLineEdit.setText(config.get(WbiConfigKey.MEDIAWIKI_API_URL))
        self.mediawikiIndexUrlLineEdit.setText(config.get(WbiConfigKey.MEDIAWIKI_INDEX_URL))
        self.mediawikiRestUrlLineEdit.setText(config.get(WbiConfigKey.MEDIAWIKI_REST_URL))
        self.sparqlEndpointUrlLineEdit.setText(config.get(WbiConfigKey.SPARQL_ENDPOINT_URL))
        self.propertyConstraintPidLineEdit.setText(config.get(WbiConfigKey.PROPERTY_CONSTRAINT_PID))
        self.instanceOfPidLineEdit.setText(config.get(ExtraWikibaseKey.INSTANCE_OF_PID))
        self.subclassOfPidLineEdit.setText(config.get(ExtraWikibaseKey.SUBCLASS_OF_PID))

    def saveConfig(self):
        config = {}
        config[WbiConfigKey.WIKIBASE_URL] = self.wikibaseUrlLineEdit.text()
        config[WbiConfigKey.DEFAULT_LANGUAGE] = self.defaultLanguageLineEdit.text()
        config[WbiConfigKey.MEDIAWIKI_API_URL] = self.mediawikiApiUrlLineEdit.text()
        config[WbiConfigKey.MEDIAWIKI_INDEX_URL] = self.mediawikiIndexUrlLineEdit.text()
        config[WbiConfigKey.MEDIAWIKI_REST_URL] = self.mediawikiRestUrlLineEdit.text()
        config[WbiConfigKey.SPARQL_ENDPOINT_URL] = self.sparqlEndpointUrlLineEdit.text()
        config[WbiConfigKey.PROPERTY_CONSTRAINT_PID] = self.propertyConstraintPidLineEdit.text()
        config[ExtraWikibaseKey.INSTANCE_OF_PID] = self.instanceOfPidLineEdit.text()
        config[ExtraWikibaseKey.SUBCLASS_OF_PID] = self.subclassOfPidLineEdit.text()
        self.model.configuration.setWikibaseConfig(config)
