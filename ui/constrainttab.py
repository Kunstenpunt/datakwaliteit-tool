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
        self.verticalLayout_3 = QVBoxLayout(ConstraintTab)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.splitter = QSplitter(ConstraintTab)
        self.splitter.setObjectName(u"splitter")
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        self.vertical_layout_widget_left = QWidget(self.splitter)
        self.vertical_layout_widget_left.setObjectName(u"vertical_layout_widget_left")
        self.vertical_layout_left = QVBoxLayout(self.vertical_layout_widget_left)
        self.vertical_layout_left.setObjectName(u"vertical_layout_left")
        self.vertical_layout_left.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_left = QHBoxLayout()
        self.horizontal_layout_left.setObjectName(u"horizontal_layout_left")
        self.label_left = QLabel(self.vertical_layout_widget_left)
        self.label_left.setObjectName(u"label_left")

        self.horizontal_layout_left.addWidget(self.label_left)

        self.horizontal_spacer_left = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontal_layout_left.addItem(self.horizontal_spacer_left)

        self.reload_button = QPushButton(self.vertical_layout_widget_left)
        self.reload_button.setObjectName(u"reload_button")

        self.horizontal_layout_left.addWidget(self.reload_button)


        self.vertical_layout_left.addLayout(self.horizontal_layout_left)

        self.properties_table_view = QTableView(self.vertical_layout_widget_left)
        self.properties_table_view.setObjectName(u"properties_table_view")
        self.properties_table_view.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.properties_table_view.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.properties_table_view.setSortingEnabled(True)

        self.vertical_layout_left.addWidget(self.properties_table_view)

        self.splitter.addWidget(self.vertical_layout_widget_left)
        self.vertical_layout_widget_right = QWidget(self.splitter)
        self.vertical_layout_widget_right.setObjectName(u"vertical_layout_widget_right")
        self.vertical_layout_right = QVBoxLayout(self.vertical_layout_widget_right)
        self.vertical_layout_right.setObjectName(u"vertical_layout_right")
        self.vertical_layout_right.setContentsMargins(0, 0, 0, 0)
        self.horizontal_layout_right = QHBoxLayout()
        self.horizontal_layout_right.setObjectName(u"horizontal_layout_right")
        self.horizontal_spacer_right_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontal_layout_right.addItem(self.horizontal_spacer_right_2)

        self.label_right = QLabel(self.vertical_layout_widget_right)
        self.label_right.setObjectName(u"label_right")
        self.label_right.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_right.setWordWrap(True)

        self.horizontal_layout_right.addWidget(self.label_right)

        self.horizontal_spacer_right = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontal_layout_right.addItem(self.horizontal_spacer_right)

        self.validate_button = QPushButton(self.vertical_layout_widget_right)
        self.validate_button.setObjectName(u"validate_button")

        self.horizontal_layout_right.addWidget(self.validate_button)


        self.vertical_layout_right.addLayout(self.horizontal_layout_right)

        self.violations_table_view = QTableView(self.vertical_layout_widget_right)
        self.violations_table_view.setObjectName(u"violations_table_view")
        self.violations_table_view.setSortingEnabled(True)

        self.vertical_layout_right.addWidget(self.violations_table_view)

        self.splitter.addWidget(self.vertical_layout_widget_right)

        self.verticalLayout_3.addWidget(self.splitter)


        self.retranslateUi(ConstraintTab)

        QMetaObject.connectSlotsByName(ConstraintTab)
    # setupUi

    def retranslateUi(self, ConstraintTab):
        ConstraintTab.setWindowTitle(QCoreApplication.translate("ConstraintTab", u"Form", None))
        self.label_left.setText(QCoreApplication.translate("ConstraintTab", u"Constrained Properties", None))
        self.reload_button.setText(QCoreApplication.translate("ConstraintTab", u"Reload", None))
        self.label_right.setText(QCoreApplication.translate("ConstraintTab", u"Selected Constrained Property\n"
"will be displayed here", None))
        self.validate_button.setText(QCoreApplication.translate("ConstraintTab", u"Validate", None))
    # retranslateUi

