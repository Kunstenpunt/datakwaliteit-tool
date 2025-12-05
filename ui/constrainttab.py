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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox, QComboBox,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QSpinBox,
    QSplitter, QTableView, QVBoxLayout, QWidget)

class Ui_ConstraintTab(object):
    def setupUi(self, ConstraintTab):
        if not ConstraintTab.objectName():
            ConstraintTab.setObjectName(u"ConstraintTab")
        ConstraintTab.resize(1323, 657)
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

        self.validateAllButton = QPushButton(self.verticalLayoutWidgetLeft)
        self.validateAllButton.setObjectName(u"validateAllButton")

        self.horizontalLayoutLeft.addWidget(self.validateAllButton)

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

        self.horizontalLayoutLeftBottom = QHBoxLayout()
        self.horizontalLayoutLeftBottom.setObjectName(u"horizontalLayoutLeftBottom")
        self.horizontalSpacerLeftBottom = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutLeftBottom.addItem(self.horizontalSpacerLeftBottom)

        self.exportAllButton = QPushButton(self.verticalLayoutWidgetLeft)
        self.exportAllButton.setObjectName(u"exportAllButton")

        self.horizontalLayoutLeftBottom.addWidget(self.exportAllButton)

        self.exportAllUrlCheckBox = QCheckBox(self.verticalLayoutWidgetLeft)
        self.exportAllUrlCheckBox.setObjectName(u"exportAllUrlCheckBox")

        self.horizontalLayoutLeftBottom.addWidget(self.exportAllUrlCheckBox)


        self.verticalLayoutLeft.addLayout(self.horizontalLayoutLeftBottom)

        self.splitter.addWidget(self.verticalLayoutWidgetLeft)
        self.verticalLayoutWidgetRight = QWidget(self.splitter)
        self.verticalLayoutWidgetRight.setObjectName(u"verticalLayoutWidgetRight")
        self.verticalLayoutRight = QVBoxLayout(self.verticalLayoutWidgetRight)
        self.verticalLayoutRight.setObjectName(u"verticalLayoutRight")
        self.verticalLayoutRight.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayoutRight = QHBoxLayout()
        self.horizontalLayoutRight.setObjectName(u"horizontalLayoutRight")
        self.horizontalSpacerRight1 = QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutRight.addItem(self.horizontalSpacerRight1)

        self.labelRight = QLabel(self.verticalLayoutWidgetRight)
        self.labelRight.setObjectName(u"labelRight")
        self.labelRight.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelRight.setWordWrap(True)
        self.labelRight.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.horizontalLayoutRight.addWidget(self.labelRight)

        self.horizontalSpacerRight2 = QSpacerItem(40, 20, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutRight.addItem(self.horizontalSpacerRight2)

        self.gridLayoutRight = QGridLayout()
        self.gridLayoutRight.setObjectName(u"gridLayoutRight")
        self.limitLabel = QLabel(self.verticalLayoutWidgetRight)
        self.limitLabel.setObjectName(u"limitLabel")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.limitLabel.sizePolicy().hasHeightForWidth())
        self.limitLabel.setSizePolicy(sizePolicy)
        self.limitLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayoutRight.addWidget(self.limitLabel, 2, 0, 1, 1)

        self.pageLabel = QLabel(self.verticalLayoutWidgetRight)
        self.pageLabel.setObjectName(u"pageLabel")
        sizePolicy.setHeightForWidth(self.pageLabel.sizePolicy().hasHeightForWidth())
        self.pageLabel.setSizePolicy(sizePolicy)
        self.pageLabel.setAlignment(Qt.AlignmentFlag.AlignRight|Qt.AlignmentFlag.AlignTrailing|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayoutRight.addWidget(self.pageLabel, 3, 0, 1, 1)

        self.limitSpinBox = QSpinBox(self.verticalLayoutWidgetRight)
        self.limitSpinBox.setObjectName(u"limitSpinBox")
        self.limitSpinBox.setMaximum(100000)
        self.limitSpinBox.setSingleStep(10000)
        self.limitSpinBox.setValue(100000)

        self.gridLayoutRight.addWidget(self.limitSpinBox, 2, 1, 1, 1)

        self.validateButton = QPushButton(self.verticalLayoutWidgetRight)
        self.validateButton.setObjectName(u"validateButton")

        self.gridLayoutRight.addWidget(self.validateButton, 3, 2, 1, 1)

        self.comboBox = QComboBox(self.verticalLayoutWidgetRight)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayoutRight.addWidget(self.comboBox, 2, 2, 1, 1)

        self.pageSpinBox = QSpinBox(self.verticalLayoutWidgetRight)
        self.pageSpinBox.setObjectName(u"pageSpinBox")
        self.pageSpinBox.setAutoFillBackground(False)
        self.pageSpinBox.setFrame(True)
        self.pageSpinBox.setMinimum(1)
        self.pageSpinBox.setValue(1)

        self.gridLayoutRight.addWidget(self.pageSpinBox, 3, 1, 1, 1)

        self.inputRowsLabel = QLabel(self.verticalLayoutWidgetRight)
        self.inputRowsLabel.setObjectName(u"inputRowsLabel")
        self.inputRowsLabel.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)

        self.gridLayoutRight.addWidget(self.inputRowsLabel, 1, 2, 1, 1)


        self.horizontalLayoutRight.addLayout(self.gridLayoutRight)


        self.verticalLayoutRight.addLayout(self.horizontalLayoutRight)

        self.violationsTableView = QTableView(self.verticalLayoutWidgetRight)
        self.violationsTableView.setObjectName(u"violationsTableView")
        self.violationsTableView.setSortingEnabled(True)

        self.verticalLayoutRight.addWidget(self.violationsTableView)

        self.horizontalLayoutRightBottom = QHBoxLayout()
        self.horizontalLayoutRightBottom.setObjectName(u"horizontalLayoutRightBottom")
        self.horizontalSpacerRightBottom = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutRightBottom.addItem(self.horizontalSpacerRightBottom)

        self.violationsLabel = QLabel(self.verticalLayoutWidgetRight)
        self.violationsLabel.setObjectName(u"violationsLabel")
        self.violationsLabel.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.horizontalLayoutRightBottom.addWidget(self.violationsLabel)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayoutRightBottom.addItem(self.horizontalSpacer)

        self.exportButton = QPushButton(self.verticalLayoutWidgetRight)
        self.exportButton.setObjectName(u"exportButton")

        self.horizontalLayoutRightBottom.addWidget(self.exportButton)

        self.exportUrlCheckBox = QCheckBox(self.verticalLayoutWidgetRight)
        self.exportUrlCheckBox.setObjectName(u"exportUrlCheckBox")

        self.horizontalLayoutRightBottom.addWidget(self.exportUrlCheckBox)


        self.verticalLayoutRight.addLayout(self.horizontalLayoutRightBottom)

        self.splitter.addWidget(self.verticalLayoutWidgetRight)

        self.verticalLayout.addWidget(self.splitter)


        self.retranslateUi(ConstraintTab)

        QMetaObject.connectSlotsByName(ConstraintTab)
    # setupUi

    def retranslateUi(self, ConstraintTab):
        ConstraintTab.setWindowTitle(QCoreApplication.translate("ConstraintTab", u"Form", None))
        self.labelLeft.setText(QCoreApplication.translate("ConstraintTab", u"Constrained Properties", None))
        self.validateAllButton.setText(QCoreApplication.translate("ConstraintTab", u"Validate All", None))
        self.reloadButton.setText(QCoreApplication.translate("ConstraintTab", u"Reload", None))
        self.exportAllButton.setText(QCoreApplication.translate("ConstraintTab", u"Export All Validated", None))
        self.exportAllUrlCheckBox.setText(QCoreApplication.translate("ConstraintTab", u"Full URLs", None))
        self.labelRight.setText(QCoreApplication.translate("ConstraintTab", u"Selected Constrained Property\n"
"will be displayed here", None))
        self.limitLabel.setText(QCoreApplication.translate("ConstraintTab", u"Limit", None))
        self.pageLabel.setText(QCoreApplication.translate("ConstraintTab", u"Page", None))
        self.validateButton.setText(QCoreApplication.translate("ConstraintTab", u"Validate", None))
        self.comboBox.setItemText(0, QCoreApplication.translate("ConstraintTab", u"Limit Output Rows", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("ConstraintTab", u"Limit Input Rows", None))

        self.inputRowsLabel.setText(QCoreApplication.translate("ConstraintTab", u"Rows to check: ?", None))
        self.violationsLabel.setText(QCoreApplication.translate("ConstraintTab", u"Not Validated", None))
        self.exportButton.setText(QCoreApplication.translate("ConstraintTab", u"Export", None))
        self.exportUrlCheckBox.setText(QCoreApplication.translate("ConstraintTab", u"Full URLs", None))
    # retranslateUi

