# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'querytab.ui'
##
## Created by: Qt User Interface Compiler version 6.10.2
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QLabel, QPlainTextEdit, QPushButton, QSizePolicy,
    QSplitter, QTableView, QVBoxLayout, QWidget)

class Ui_QueryTab(object):
    def setupUi(self, QueryTab): # type: ignore
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
        self.horizontalLayoutTopLeft = QHBoxLayout()
        self.horizontalLayoutTopLeft.setObjectName(u"horizontalLayoutTopLeft")
        self.labelLeft = QLabel(self.verticalLayoutWidget)
        self.labelLeft.setObjectName(u"labelLeft")
        self.labelLeft.setWordWrap(True)

        self.horizontalLayoutTopLeft.addWidget(self.labelLeft)

        self.clearButton = QPushButton(self.verticalLayoutWidget)
        self.clearButton.setObjectName(u"clearButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.clearButton.sizePolicy().hasHeightForWidth())
        self.clearButton.setSizePolicy(sizePolicy)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditDelete))
        self.clearButton.setIcon(icon)

        self.horizontalLayoutTopLeft.addWidget(self.clearButton, 0, Qt.AlignmentFlag.AlignBottom)

        self.copyButton = QPushButton(self.verticalLayoutWidget)
        self.copyButton.setObjectName(u"copyButton")
        sizePolicy.setHeightForWidth(self.copyButton.sizePolicy().hasHeightForWidth())
        self.copyButton.setSizePolicy(sizePolicy)
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        self.copyButton.setIcon(icon1)

        self.horizontalLayoutTopLeft.addWidget(self.copyButton, 0, Qt.AlignmentFlag.AlignBottom)

        self.pasteButton = QPushButton(self.verticalLayoutWidget)
        self.pasteButton.setObjectName(u"pasteButton")
        sizePolicy.setHeightForWidth(self.pasteButton.sizePolicy().hasHeightForWidth())
        self.pasteButton.setSizePolicy(sizePolicy)
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditPaste))
        self.pasteButton.setIcon(icon2)

        self.horizontalLayoutTopLeft.addWidget(self.pasteButton, 0, Qt.AlignmentFlag.AlignBottom)


        self.verticalLayoutLeft.addLayout(self.horizontalLayoutTopLeft)

        self.plainTextEdit = QPlainTextEdit(self.verticalLayoutWidget)
        self.plainTextEdit.setObjectName(u"plainTextEdit")

        self.verticalLayoutLeft.addWidget(self.plainTextEdit)

        self.horizontalLayoutBottomLeft = QHBoxLayout()
        self.horizontalLayoutBottomLeft.setObjectName(u"horizontalLayoutBottomLeft")
        self.executeButton = QPushButton(self.verticalLayoutWidget)
        self.executeButton.setObjectName(u"executeButton")

        self.horizontalLayoutBottomLeft.addWidget(self.executeButton)


        self.verticalLayoutLeft.addLayout(self.horizontalLayoutBottomLeft)

        self.splitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget2 = QWidget(self.splitter)
        self.verticalLayoutWidget2.setObjectName(u"verticalLayoutWidget2")
        self.verticalLayoutRight = QVBoxLayout(self.verticalLayoutWidget2)
        self.verticalLayoutRight.setObjectName(u"verticalLayoutRight")
        self.verticalLayoutRight.setContentsMargins(0, 0, 0, 0)
        self.tableView = QTableView(self.verticalLayoutWidget2)
        self.tableView.setObjectName(u"tableView")
        self.tableView.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableView.setSortingEnabled(True)
        self.tableView.horizontalHeader().setStretchLastSection(True)

        self.verticalLayoutRight.addWidget(self.tableView)

        self.splitter.addWidget(self.verticalLayoutWidget2)

        self.horizontalLayout.addWidget(self.splitter)


        self.retranslateUi(QueryTab) # type: ignore
        self.pasteButton.clicked.connect(self.plainTextEdit.paste)
        self.clearButton.clicked.connect(self.plainTextEdit.clear)

        QMetaObject.connectSlotsByName(QueryTab)
    # setupUi

    def retranslateUi(self, QueryTab): # type: ignore
        QueryTab.setWindowTitle(QCoreApplication.translate("QueryTab", u"Form", None))
        self.labelLeft.setText(QCoreApplication.translate("QueryTab", u"Fill in the SPARQL query you want to execute.", None))
#if QT_CONFIG(tooltip)
        self.clearButton.setToolTip(QCoreApplication.translate("QueryTab", u"Clear Query", None))
#endif // QT_CONFIG(tooltip)
        self.clearButton.setText("")
#if QT_CONFIG(tooltip)
        self.copyButton.setToolTip(QCoreApplication.translate("QueryTab", u"Copy Query", None))
#endif // QT_CONFIG(tooltip)
        self.copyButton.setText("")
#if QT_CONFIG(tooltip)
        self.pasteButton.setToolTip(QCoreApplication.translate("QueryTab", u"Paste Query", None))
#endif // QT_CONFIG(tooltip)
        self.pasteButton.setText("")
        self.executeButton.setText(QCoreApplication.translate("QueryTab", u"Execute", None))
    # retranslateUi

