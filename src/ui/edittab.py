from PySide6.QtWidgets import QWidget

from .designer.edittab import Ui_EditTab


class EditTab(QWidget, Ui_EditTab):
    def __init__(self, model):
        super().__init__()
        self.setupUi(self)

        self.model = model
