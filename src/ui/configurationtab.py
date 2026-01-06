from PySide6.QtWidgets import QWidget

from .designer.configurationtab import Ui_ConfigurationTab


class ConfigurationTab(QWidget, Ui_ConfigurationTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model
