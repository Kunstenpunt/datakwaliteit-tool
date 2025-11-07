# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'queryform.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPlainTextEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_QueryForm(object):
    def setupUi(self, QueryForm):
        if not QueryForm.objectName():
            QueryForm.setObjectName(u"QueryForm")
        QueryForm.resize(396, 336)
        self.verticalLayout_2 = QVBoxLayout(QueryForm)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(QueryForm)
        self.label.setObjectName(u"label")
        self.label.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.label)

        self.plainTextEdit = QPlainTextEdit(QueryForm)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.verticalLayout_2.addWidget(self.plainTextEdit)

        self.buttonHorizontalLayout = QHBoxLayout()
        self.buttonHorizontalLayout.setObjectName(u"buttonHorizontalLayout")
        self.clearButton = QPushButton(QueryForm)
        self.clearButton.setObjectName(u"clearButton")

        self.buttonHorizontalLayout.addWidget(self.clearButton)

        self.executeButton = QPushButton(QueryForm)
        self.executeButton.setObjectName(u"executeButton")

        self.buttonHorizontalLayout.addWidget(self.executeButton)


        self.verticalLayout_2.addLayout(self.buttonHorizontalLayout)


        self.retranslateUi(QueryForm)
        self.clearButton.clicked.connect(self.plainTextEdit.clear)

        QMetaObject.connectSlotsByName(QueryForm)
    # setupUi

    def retranslateUi(self, QueryForm):
        QueryForm.setWindowTitle(QCoreApplication.translate("QueryForm", u"Form", None))
        self.label.setText(QCoreApplication.translate("QueryForm", u"Fill in the SPARQL query you want to execute.", None))
        self.clearButton.setText(QCoreApplication.translate("QueryForm", u"Clear", None))
        self.executeButton.setText(QCoreApplication.translate("QueryForm", u"Execute", None))
    # retranslateUi

