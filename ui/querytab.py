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
        self.vertical_layout_left = QVBoxLayout(self.verticalLayoutWidget)
        self.vertical_layout_left.setObjectName(u"vertical_layout_left")
        self.vertical_layout_left.setContentsMargins(0, 0, 0, 0)
        self.label = QLabel(self.verticalLayoutWidget)
        self.label.setObjectName(u"label")
        self.label.setWordWrap(True)

        self.vertical_layout_left.addWidget(self.label)

        self.plain_text_edit = QPlainTextEdit(self.verticalLayoutWidget)
        self.plain_text_edit.setObjectName(u"plain_text_edit")

        self.vertical_layout_left.addWidget(self.plain_text_edit)

        self.button_horizontal_layout = QHBoxLayout()
        self.button_horizontal_layout.setObjectName(u"button_horizontal_layout")
        self.clear_button = QPushButton(self.verticalLayoutWidget)
        self.clear_button.setObjectName(u"clear_button")

        self.button_horizontal_layout.addWidget(self.clear_button)

        self.execute_button = QPushButton(self.verticalLayoutWidget)
        self.execute_button.setObjectName(u"execute_button")

        self.button_horizontal_layout.addWidget(self.execute_button)


        self.vertical_layout_left.addLayout(self.button_horizontal_layout)

        self.splitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget_2 = QWidget(self.splitter)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        self.vertical_layout_right = QVBoxLayout(self.verticalLayoutWidget_2)
        self.vertical_layout_right.setObjectName(u"vertical_layout_right")
        self.vertical_layout_right.setContentsMargins(0, 0, 0, 0)
        self.table_view = QTableView(self.verticalLayoutWidget_2)
        self.table_view.setObjectName(u"table_view")
        self.table_view.setSortingEnabled(True)
        self.table_view.horizontalHeader().setStretchLastSection(True)

        self.vertical_layout_right.addWidget(self.table_view)

        self.splitter.addWidget(self.verticalLayoutWidget_2)

        self.horizontalLayout.addWidget(self.splitter)


        self.retranslateUi(QueryTab)

        QMetaObject.connectSlotsByName(QueryTab)
    # setupUi

    def retranslateUi(self, QueryTab):
        QueryTab.setWindowTitle(QCoreApplication.translate("QueryTab", u"Form", None))
        self.label.setText(QCoreApplication.translate("QueryTab", u"Fill in the SPARQL query you want to execute.", None))
        self.clear_button.setText(QCoreApplication.translate("QueryTab", u"Clear", None))
        self.execute_button.setText(QCoreApplication.translate("QueryTab", u"Execute", None))
    # retranslateUi

