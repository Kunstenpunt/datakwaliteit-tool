# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'constrainttab.ui'
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QHBoxLayout, QHeaderView,
    QLabel, QPushButton, QSizePolicy, QSpacerItem,
    QSplitter, QTableView, QVBoxLayout, QWidget)

class Ui_ConstraintTab(object):
    def setupUi(self, ConstraintTab):
        if not ConstraintTab.objectName():
            ConstraintTab.setObjectName(u"ConstraintTab")
        ConstraintTab.resize(980, 657)
        self.verticalLayout = QVBoxLayout(ConstraintTab)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.splitter = QSplitter(ConstraintTab)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.verticalLayoutWidgetLeft = QWidget(self.splitter)
        self.verticalLayoutWidgetLeft.setObjectName(u"verticalLayoutWidgetLeft")
        self.verticalLayoutLeft = QVBoxLayout(self.verticalLayoutWidgetLeft)
        self.verticalLayoutLeft.setObjectName(u"verticalLayoutLeft")
        self.verticalLayoutLeft.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutLeft = QHBoxLayout()
        self.horizontalLayoutLeft.setObjectName(u"horizontalLayoutLeft")
        self.labelLeft = QLabel(self.verticalLayoutWidgetLeft)
        self.labelLeft.setObjectName(u"labelLeft")

        self.horizontalLayoutLeft.addWidget(self.labelLeft)

        self.horizontalSpacerLeft = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutLeft.addItem(self.horizontalSpacerLeft)

        self.reloadButton = QPushButton(self.verticalLayoutWidgetLeft)
        self.reloadButton.setObjectName(u"reloadButton")

        self.horizontalLayoutLeft.addWidget(self.reloadButton)


        self.verticalLayoutLeft.addLayout(self.horizontalLayoutLeft)

        self.propertiesTableView = QTableView(self.verticalLayoutWidgetLeft)
        self.propertiesTableView.setObjectName(u"propertiesTableView")
        self.propertiesTableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.propertiesTableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.propertiesTableView.setSortingEnabled(True)

        self.verticalLayoutLeft.addWidget(self.propertiesTableView)

        self.splitter.addWidget(self.verticalLayoutWidgetLeft)
        self.verticalLayoutWidgetRight = QWidget(self.splitter)
        self.verticalLayoutWidgetRight.setObjectName(u"verticalLayoutWidgetRight")
        self.verticalLayoutRight = QVBoxLayout(self.verticalLayoutWidgetRight)
        self.verticalLayoutRight.setObjectName(u"verticalLayoutRight")
        self.verticalLayoutRight.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutRight = QHBoxLayout()
        self.horizontalLayoutRight.setObjectName(u"horizontalLayoutRight")
        self.horizontalSpacerRight1 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutRight.addItem(self.horizontalSpacerRight1)

        self.labelRight = QLabel(self.verticalLayoutWidgetRight)
        self.labelRight.setObjectName(u"labelRight")
        self.labelRight.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelRight.setWordWrap(True)

        self.horizontalLayoutRight.addWidget(self.labelRight)

        self.horizontalSpacerRight2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutRight.addItem(self.horizontalSpacerRight2)

        self.validateButton = QPushButton(self.verticalLayoutWidgetRight)
        self.validateButton.setObjectName(u"validateButton")

        self.horizontalLayoutRight.addWidget(self.validateButton)


        self.verticalLayoutRight.addLayout(self.horizontalLayoutRight)

        self.violationsTableView = QTableView(self.verticalLayoutWidgetRight)
        self.violationsTableView.setObjectName(u"violationsTableView")
        self.violationsTableView.setSortingEnabled(True)

        self.verticalLayoutRight.addWidget(self.violationsTableView)

        self.splitter.addWidget(self.verticalLayoutWidgetRight)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(ConstraintTab)

        QMetaObject.connectSlotsByName(ConstraintTab)
    # setupUi

    def retranslateUi(self, ConstraintTab):
        ConstraintTab.setWindowTitle(QCoreApplication.translate("ConstraintTab", u"Form", None))
        self.labelLeft.setText(QCoreApplication.translate("ConstraintTab", u"Constrained Properties", None))
        self.reloadButton.setText(QCoreApplication.translate("ConstraintTab", u"Reload", None))
        self.labelRight.setText(QCoreApplication.translate("ConstraintTab", u"Selected Constrained Property\n"
"will be displayed here", None))
        self.validateButton.setText(QCoreApplication.translate("ConstraintTab", u"Validate", None))
    # retranslateUi

