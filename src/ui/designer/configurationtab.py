# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'configurationtab.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_ConfigurationTab(object):
    def setupUi(self, ConfigurationTab):
        if not ConfigurationTab.objectName():
            ConfigurationTab.setObjectName(u"ConfigurationTab")
        ConfigurationTab.resize(701, 567)
        self.verticalLayout_2 = QVBoxLayout(ConfigurationTab)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.wikibaseConfigTitleLabel = QLabel(ConfigurationTab)
        self.wikibaseConfigTitleLabel.setObjectName(u"wikibaseConfigTitleLabel")
        self.wikibaseConfigTitleLabel.setTextFormat(Qt.TextFormat.MarkdownText)

        self.verticalLayout.addWidget(self.wikibaseConfigTitleLabel)

        self.wikibaseConfigurationFormLayout = QFormLayout()
        self.wikibaseConfigurationFormLayout.setObjectName(u"wikibaseConfigurationFormLayout")
        self.wikibaseConfigurationFormLayout.setFieldGrowthPolicy(QFormLayout.FieldGrowthPolicy.AllNonFixedFieldsGrow)
        self.wikibaseUrlLabel = QLabel(ConfigurationTab)
        self.wikibaseUrlLabel.setObjectName(u"wikibaseUrlLabel")

        self.wikibaseConfigurationFormLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.wikibaseUrlLabel)

        self.wikibaseUrlLineEdit = QLineEdit(ConfigurationTab)
        self.wikibaseUrlLineEdit.setObjectName(u"wikibaseUrlLineEdit")

        self.wikibaseConfigurationFormLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.wikibaseUrlLineEdit)

        self.defaultLanguageLabel = QLabel(ConfigurationTab)
        self.defaultLanguageLabel.setObjectName(u"defaultLanguageLabel")

        self.wikibaseConfigurationFormLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.defaultLanguageLabel)

        self.defaultLanguageLineEdit = QLineEdit(ConfigurationTab)
        self.defaultLanguageLineEdit.setObjectName(u"defaultLanguageLineEdit")

        self.wikibaseConfigurationFormLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.defaultLanguageLineEdit)

        self.mediawikiApiUrlLabel = QLabel(ConfigurationTab)
        self.mediawikiApiUrlLabel.setObjectName(u"mediawikiApiUrlLabel")

        self.wikibaseConfigurationFormLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.mediawikiApiUrlLabel)

        self.mediawikiApiUrlLineEdit = QLineEdit(ConfigurationTab)
        self.mediawikiApiUrlLineEdit.setObjectName(u"mediawikiApiUrlLineEdit")

        self.wikibaseConfigurationFormLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.mediawikiApiUrlLineEdit)

        self.mediawikiIndexUrlLabel = QLabel(ConfigurationTab)
        self.mediawikiIndexUrlLabel.setObjectName(u"mediawikiIndexUrlLabel")

        self.wikibaseConfigurationFormLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.mediawikiIndexUrlLabel)

        self.mediawikiIndexUrlLineEdit = QLineEdit(ConfigurationTab)
        self.mediawikiIndexUrlLineEdit.setObjectName(u"mediawikiIndexUrlLineEdit")

        self.wikibaseConfigurationFormLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.mediawikiIndexUrlLineEdit)

        self.mediawikiRestUrlLabel = QLabel(ConfigurationTab)
        self.mediawikiRestUrlLabel.setObjectName(u"mediawikiRestUrlLabel")

        self.wikibaseConfigurationFormLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.mediawikiRestUrlLabel)

        self.mediawikiRestUrlLineEdit = QLineEdit(ConfigurationTab)
        self.mediawikiRestUrlLineEdit.setObjectName(u"mediawikiRestUrlLineEdit")

        self.wikibaseConfigurationFormLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.mediawikiRestUrlLineEdit)

        self.sparqlEndpointUrlLabel = QLabel(ConfigurationTab)
        self.sparqlEndpointUrlLabel.setObjectName(u"sparqlEndpointUrlLabel")

        self.wikibaseConfigurationFormLayout.setWidget(5, QFormLayout.ItemRole.LabelRole, self.sparqlEndpointUrlLabel)

        self.sparqlEndpointUrlLineEdit = QLineEdit(ConfigurationTab)
        self.sparqlEndpointUrlLineEdit.setObjectName(u"sparqlEndpointUrlLineEdit")

        self.wikibaseConfigurationFormLayout.setWidget(5, QFormLayout.ItemRole.FieldRole, self.sparqlEndpointUrlLineEdit)

        self.propertyConstraintPidLabel = QLabel(ConfigurationTab)
        self.propertyConstraintPidLabel.setObjectName(u"propertyConstraintPidLabel")

        self.wikibaseConfigurationFormLayout.setWidget(6, QFormLayout.ItemRole.LabelRole, self.propertyConstraintPidLabel)

        self.instanceOfPidLabel = QLabel(ConfigurationTab)
        self.instanceOfPidLabel.setObjectName(u"instanceOfPidLabel")

        self.wikibaseConfigurationFormLayout.setWidget(7, QFormLayout.ItemRole.LabelRole, self.instanceOfPidLabel)

        self.propertyConstraintPidLineEdit = QLineEdit(ConfigurationTab)
        self.propertyConstraintPidLineEdit.setObjectName(u"propertyConstraintPidLineEdit")

        self.wikibaseConfigurationFormLayout.setWidget(6, QFormLayout.ItemRole.FieldRole, self.propertyConstraintPidLineEdit)

        self.instanceOfPidLineEdit = QLineEdit(ConfigurationTab)
        self.instanceOfPidLineEdit.setObjectName(u"instanceOfPidLineEdit")

        self.wikibaseConfigurationFormLayout.setWidget(7, QFormLayout.ItemRole.FieldRole, self.instanceOfPidLineEdit)

        self.subclassOfPidLabel = QLabel(ConfigurationTab)
        self.subclassOfPidLabel.setObjectName(u"subclassOfPidLabel")

        self.wikibaseConfigurationFormLayout.setWidget(8, QFormLayout.ItemRole.LabelRole, self.subclassOfPidLabel)

        self.subclassOfPidLineEdit = QLineEdit(ConfigurationTab)
        self.subclassOfPidLineEdit.setObjectName(u"subclassOfPidLineEdit")

        self.wikibaseConfigurationFormLayout.setWidget(8, QFormLayout.ItemRole.FieldRole, self.subclassOfPidLineEdit)


        self.verticalLayout.addLayout(self.wikibaseConfigurationFormLayout)

        self.botLoginTitleLabel = QLabel(ConfigurationTab)
        self.botLoginTitleLabel.setObjectName(u"botLoginTitleLabel")
        self.botLoginTitleLabel.setTextFormat(Qt.TextFormat.MarkdownText)

        self.verticalLayout.addWidget(self.botLoginTitleLabel)

        self.botLoginFormLayout = QFormLayout()
        self.botLoginFormLayout.setObjectName(u"botLoginFormLayout")
        self.botUsernameLabel = QLabel(ConfigurationTab)
        self.botUsernameLabel.setObjectName(u"botUsernameLabel")

        self.botLoginFormLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.botUsernameLabel)

        self.botPasswordLabel = QLabel(ConfigurationTab)
        self.botPasswordLabel.setObjectName(u"botPasswordLabel")

        self.botLoginFormLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.botPasswordLabel)

        self.botUsernameLineEdit = QLineEdit(ConfigurationTab)
        self.botUsernameLineEdit.setObjectName(u"botUsernameLineEdit")

        self.botLoginFormLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.botUsernameLineEdit)

        self.botPasswordLineEdit = QLineEdit(ConfigurationTab)
        self.botPasswordLineEdit.setObjectName(u"botPasswordLineEdit")

        self.botLoginFormLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.botPasswordLineEdit)


        self.verticalLayout.addLayout(self.botLoginFormLayout)


        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.buttonHorizontalLayout = QHBoxLayout()
        self.buttonHorizontalLayout.setObjectName(u"buttonHorizontalLayout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.buttonHorizontalLayout.addItem(self.horizontalSpacer)

        self.discardButton = QPushButton(ConfigurationTab)
        self.discardButton.setObjectName(u"discardButton")

        self.buttonHorizontalLayout.addWidget(self.discardButton)

        self.saveButton = QPushButton(ConfigurationTab)
        self.saveButton.setObjectName(u"saveButton")

        self.buttonHorizontalLayout.addWidget(self.saveButton)


        self.verticalLayout_2.addLayout(self.buttonHorizontalLayout)


        self.retranslateUi(ConfigurationTab)

        QMetaObject.connectSlotsByName(ConfigurationTab)
    # setupUi

    def retranslateUi(self, ConfigurationTab):
        ConfigurationTab.setWindowTitle(QCoreApplication.translate("ConfigurationTab", u"Form", None))
        self.wikibaseConfigTitleLabel.setText(QCoreApplication.translate("ConfigurationTab", u"### Wikibase Configuration", None))
        self.wikibaseUrlLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Wikibase URL", None))
        self.wikibaseUrlLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"https://www.wikidata.org", None))
        self.defaultLanguageLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Default Language", None))
        self.defaultLanguageLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"en", None))
        self.mediawikiApiUrlLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Mediawiki API URL", None))
        self.mediawikiApiUrlLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"https://www.wikidata.org/w/api.php", None))
        self.mediawikiIndexUrlLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Mediawiki Index URL", None))
        self.mediawikiIndexUrlLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"https://www.wikidata.org/w/index.php", None))
        self.mediawikiRestUrlLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Mediawiki REST URL", None))
        self.mediawikiRestUrlLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"https://www.wikidata.org/w/rest.php", None))
        self.sparqlEndpointUrlLabel.setText(QCoreApplication.translate("ConfigurationTab", u"SPARQL Endpoint URL", None))
        self.sparqlEndpointUrlLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"https://query.wikidata.org/sparql", None))
        self.propertyConstraintPidLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Property Constraint PID", None))
        self.instanceOfPidLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Instance Of PID", None))
        self.propertyConstraintPidLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"P2302", None))
        self.instanceOfPidLineEdit.setText("")
        self.instanceOfPidLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"P31", None))
        self.subclassOfPidLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Subclass Of PID", None))
        self.subclassOfPidLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"P279", None))
        self.botLoginTitleLabel.setText(QCoreApplication.translate("ConfigurationTab", u"### Bot Login (needed for QuickStatements)", None))
        self.botUsernameLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Bot Username", None))
        self.botPasswordLabel.setText(QCoreApplication.translate("ConfigurationTab", u"Bot Password", None))
        self.botUsernameLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"USERNAME@BOT", None))
        self.botPasswordLineEdit.setPlaceholderText(QCoreApplication.translate("ConfigurationTab", u"PASSWORD", None))
        self.discardButton.setText(QCoreApplication.translate("ConfigurationTab", u"Discard Changes", None))
        self.saveButton.setText(QCoreApplication.translate("ConfigurationTab", u"Save", None))
    # retranslateUi

