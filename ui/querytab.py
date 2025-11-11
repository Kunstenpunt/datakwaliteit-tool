# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'querytab.ui'
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QLabel,
    QPlainTextEdit, QPushButton, QSizePolicy, QSplitter,
    QTableView, QVBoxLayout, QWidget)

class Ui_QueryTab(object):
    def setupUi(self, QueryTab):
        if not QueryTab.objectName():
            QueryTab.setObjectName(u"QueryTab")
        QueryTab.resize(746, 567)
        self.horizontalLayout = QHBoxLayout(QueryTab)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.splitter = QSplitter(QueryTab)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutLeft = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayoutLeft.setObjectName(u"verticalLayoutLeft")
        self.verticalLayoutLeft.setContentsMargins(0, 0, 0, 0)
        self.labelLeft = QLabel(self.verticalLayoutWidget)
        self.labelLeft.setObjectName(u"labelLeft")
        self.labelLeft.setWordWrap(True)

        self.verticalLayoutLeft.addWidget(self.labelLeft)

        self.plainTextEdit = QPlainTextEdit(self.verticalLayoutWidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.verticalLayoutLeft.addWidget(self.plainTextEdit)

        self.buttonHorizontalLayout = QHBoxLayout()
        self.buttonHorizontalLayout.setObjectName(u"buttonHorizontalLayout")
        self.clearButton = QPushButton(self.verticalLayoutWidget)
        self.clearButton.setObjectName(u"clearButton")

        self.buttonHorizontalLayout.addWidget(self.clearButton)

        self.executeButton = QPushButton(self.verticalLayoutWidget)
        self.executeButton.setObjectName(u"executeButton")

        self.buttonHorizontalLayout.addWidget(self.executeButton)


        self.verticalLayoutLeft.addLayout(self.buttonHorizontalLayout)

        self.splitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget2 = QWidget(self.splitter)
        self.verticalLayoutWidget2.setObjectName(u"verticalLayoutWidget2")
        self.verticalLayoutRight = QVBoxLayout(self.verticalLayoutWidget2)
        self.verticalLayoutRight.setObjectName(u"verticalLayoutRight")
        self.verticalLayoutRight.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView(self.verticalLayoutWidget2)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.verticalLayoutRight.addWidget(self.tableView)

        self.splitter.addWidget(self.verticalLayoutWidget2)

        self.horizontalLayout.addWidget(self.splitter)


        self.retranslateUi(QueryTab)
        self.clearButton.clicked.connect(self.plainTextEdit.clear)

        QMetaObject.connectSlotsByName(QueryTab)
    # setupUi

    def retranslateUi(self, QueryTab):
        QueryTab.setWindowTitle(QCoreApplication.translate("QueryTab", u"Form", None))
        self.labelLeft.setText(QCoreApplication.translate("QueryTab", u"Fill in the SPARQL query you want to execute.", None))
        self.clearButton.setText(QCoreApplication.translate("QueryTab", u"Clear", None))
        self.executeButton.setText(QCoreApplication.translate("QueryTab", u"Execute", None))
    # retranslateUi

