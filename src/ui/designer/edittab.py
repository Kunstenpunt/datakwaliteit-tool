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
    def setupUi(self, EditTab): # type: ignore
        if not EditTab.objectName():
            EditTab.setObjectName(u"EditTab")
        EditTab.resize(860, 536)
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
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.inputQueryLabel = QLabel(self.verticalLayoutWidget)
        self.inputQueryLabel.setObjectName(u"inputQueryLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.inputQueryLabel.sizePolicy().hasHeightForWidth())
        self.inputQueryLabel.setSizePolicy(sizePolicy)
        self.inputQueryLabel.setTextFormat(Qt.TextFormat.MarkdownText)
        self.inputQueryLabel.setScaledContents(False)
        self.inputQueryLabel.setWordWrap(True)

        self.horizontalLayout_3.addWidget(self.inputQueryLabel)

        self.clearButton = QPushButton(self.verticalLayoutWidget)
        self.clearButton.setObjectName(u"clearButton")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.clearButton.sizePolicy().hasHeightForWidth())
        self.clearButton.setSizePolicy(sizePolicy1)
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditDelete))
        self.clearButton.setIcon(icon)
        self.clearButton.setFlat(False)

        self.horizontalLayout_3.addWidget(self.clearButton, 0, Qt.AlignmentFlag.AlignBottom)

        self.copyButton = QPushButton(self.verticalLayoutWidget)
        self.copyButton.setObjectName(u"copyButton")
        sizePolicy1.setHeightForWidth(self.copyButton.sizePolicy().hasHeightForWidth())
        self.copyButton.setSizePolicy(sizePolicy1)
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        self.copyButton.setIcon(icon1)

        self.horizontalLayout_3.addWidget(self.copyButton, 0, Qt.AlignmentFlag.AlignBottom)

        self.pasteButton = QPushButton(self.verticalLayoutWidget)
        self.pasteButton.setObjectName(u"pasteButton")
        sizePolicy1.setHeightForWidth(self.pasteButton.sizePolicy().hasHeightForWidth())
        self.pasteButton.setSizePolicy(sizePolicy1)
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditPaste))
        self.pasteButton.setIcon(icon2)

        self.horizontalLayout_3.addWidget(self.pasteButton, 0, Qt.AlignmentFlag.AlignBottom)


        self.verticalLayout.addLayout(self.horizontalLayout_3)

        self.queryPlainTextEdit = QPlainTextEdit(self.verticalLayoutWidget)
        self.queryPlainTextEdit.setObjectName(u"queryPlainTextEdit")

        self.verticalLayout.addWidget(self.queryPlainTextEdit)

        self.line = QFrame(self.verticalLayoutWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line)

        self.modificationRecipeLabel = QLabel(self.verticalLayoutWidget)
        self.modificationRecipeLabel.setObjectName(u"modificationRecipeLabel")
        self.modificationRecipeLabel.setTextFormat(Qt.TextFormat.MarkdownText)
        self.modificationRecipeLabel.setWordWrap(True)

        self.verticalLayout.addWidget(self.modificationRecipeLabel)

        self.recipePlainTextEdit = QPlainTextEdit(self.verticalLayoutWidget)
        self.recipePlainTextEdit.setObjectName(u"recipePlainTextEdit")

        self.verticalLayout.addWidget(self.recipePlainTextEdit)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.generateButton = QPushButton(self.verticalLayoutWidget)
        self.generateButton.setObjectName(u"generateButton")

        self.horizontalLayout_2.addWidget(self.generateButton)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.splitter.addWidget(self.verticalLayoutWidget)
        self.verticalLayoutWidget2 = QWidget(self.splitter)
        self.verticalLayoutWidget2.setObjectName(u"verticalLayoutWidget2")
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.generatedStatementsLabel = QLabel(self.verticalLayoutWidget2)
        self.generatedStatementsLabel.setObjectName(u"generatedStatementsLabel")
        self.generatedStatementsLabel.setTextFormat(Qt.TextFormat.MarkdownText)

        self.horizontalLayout_4.addWidget(self.generatedStatementsLabel)

        self.copyStatementsButton = QPushButton(self.verticalLayoutWidget2)
        self.copyStatementsButton.setObjectName(u"copyStatementsButton")
        sizePolicy1.setHeightForWidth(self.copyStatementsButton.sizePolicy().hasHeightForWidth())
        self.copyStatementsButton.setSizePolicy(sizePolicy1)
        self.copyStatementsButton.setIcon(icon1)

        self.horizontalLayout_4.addWidget(self.copyStatementsButton, 0, Qt.AlignmentFlag.AlignBottom)


        self.verticalLayout_2.addLayout(self.horizontalLayout_4)

        self.statementsPlainTextEdit = QPlainTextEdit(self.verticalLayoutWidget2)
        self.statementsPlainTextEdit.setObjectName(u"statementsPlainTextEdit")

        self.verticalLayout_2.addWidget(self.statementsPlainTextEdit)

        self.splitter.addWidget(self.verticalLayoutWidget2)

        self.horizontalLayout.addWidget(self.splitter)


        self.retranslateUi(EditTab) # type: ignore
        self.clearButton.clicked.connect(self.queryPlainTextEdit.clear)
        self.pasteButton.clicked.connect(self.queryPlainTextEdit.paste)

        QMetaObject.connectSlotsByName(EditTab)
    # setupUi

    def retranslateUi(self, EditTab): # type: ignore
        EditTab.setWindowTitle(QCoreApplication.translate("EditTab", u"Form", None))
        self.inputQueryLabel.setText(QCoreApplication.translate("EditTab", u"### Input Query\n"
"The results of this query will be used to make modifications.", None))
#if QT_CONFIG(tooltip)
        self.clearButton.setToolTip(QCoreApplication.translate("EditTab", u"Clear Query", None))
#endif // QT_CONFIG(tooltip)
        self.clearButton.setText("")
#if QT_CONFIG(tooltip)
        self.copyButton.setToolTip(QCoreApplication.translate("EditTab", u"Copy Query", None))
#endif // QT_CONFIG(tooltip)
        self.copyButton.setText("")
#if QT_CONFIG(tooltip)
        self.pasteButton.setToolTip(QCoreApplication.translate("EditTab", u"Paste Query", None))
#endif // QT_CONFIG(tooltip)
        self.pasteButton.setText("")
        self.modificationRecipeLabel.setText(QCoreApplication.translate("EditTab", u"### Modification Recipe\n"
"For each returned row of the Input Query, perform the following modifications (basic QuickStatements syntax). Use *?variable* to access specific fields of the query results.", None))
        self.generateButton.setText(QCoreApplication.translate("EditTab", u"Generate All Statements", None))
        self.generatedStatementsLabel.setText(QCoreApplication.translate("EditTab", u"### Generated Statements\n"
"These are in QuickStatements **V1 command** format.", None))
#if QT_CONFIG(tooltip)
        self.copyStatementsButton.setToolTip(QCoreApplication.translate("EditTab", u"Copy Statements", None))
#endif // QT_CONFIG(tooltip)
        self.copyStatementsButton.setText("")
    # retranslateUi

