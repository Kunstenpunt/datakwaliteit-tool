# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edittab.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPlainTextEdit, QPushButton, QSizePolicy, QSplitter,
    QVBoxLayout, QWidget)

class Ui_EditTab(object):
    def setupUi(self, EditTab):
        if not EditTab.objectName():
            EditTab.setObjectName(u"EditTab")
        EditTab.resize(797, 536)
        self.horizontalLayout = QHBoxLayout(EditTab)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.splitter = QSplitter(EditTab)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.verticalLayoutWidget = QWidget(self.splitter)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")
        self.label.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label.setScaledContents(False)
        self.label.setWordWrap(True)

        self.verticalLayout.addWidget(self.label)

        self.plainTextEdit = QPlainTextEdit(self.verticalLayoutWidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.verticalLayout.addWidget(self.plainTextEdit)

        self.line = QFrame(self.verticalLayoutWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.label_2 = QLabel(self.verticalLayoutWidget)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setTextFormat(Qt.TextFormat.MarkdownText)
        self.label_2.setWordWrap(True)

        self.verticalLayout.addWidget(self.label_2)

        self.plainTextEdit_2 = QPlainTextEdit(self.verticalLayoutWidget)
        self.plainTextEdit_2.setObjectName(u"plainTextEdit_2")

        self.verticalLayout.addWidget(self.plainTextEdit_2)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.pushButton = QPushButton(self.verticalLayoutWidget)
        self.pushButton.setObjectName(u"pushButton")

        self.horizontalLayout_2.addWidget(self.pushButton)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.splitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget2 = QWidget(self.splitter)
        self.verticalLayoutWidget2.setObjectName(u"verticalLayoutWidget2")
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.label_3 = QLabel(self.verticalLayoutWidget2)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setTextFormat(Qt.TextFormat.MarkdownText)

        self.verticalLayout_2.addWidget(self.label_3)

        self.plainTextEdit_3 = QPlainTextEdit(self.verticalLayoutWidget2)
        self.plainTextEdit_3.setObjectName(u"plainTextEdit_3")

        self.verticalLayout_2.addWidget(self.plainTextEdit_3)

        self.splitter.addWidget(self.verticalLayoutWidget2)

        self.horizontalLayout.addWidget(self.splitter)


        self.retranslateUi(EditTab)

        QMetaObject.connectSlotsByName(EditTab)
    # setupUi

    def retranslateUi(self, EditTab):
        EditTab.setWindowTitle(QCoreApplication.translate("EditTab", u"Form", None))
        self.label.setText(QCoreApplication.translate("EditTab", u"### Input Query\n"
"The results of this query will be used to make modifications.", None))
        self.label_2.setText(QCoreApplication.translate("EditTab", u"### Modification Recipe\n"
"For each returned row of the Input Query, perform the following modifications (basic QuickStatements syntax). Use *?variable* to access specific fields of the query results.", None))
        self.pushButton.setText(QCoreApplication.translate("EditTab", u"Generate All Modifications", None))
        self.label_3.setText(QCoreApplication.translate("EditTab", u"### Generated Modifications", None))
    # retranslateUi

