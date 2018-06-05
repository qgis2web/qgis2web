# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_maindialog.ui'
#
# Created: Thu Jan 12 14:45:12 2017
#      by: PyQt4 UI code generator 4.10.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from .ui_timedialog import Ui_TimeDialog

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)


class Ui_MainDialog(object):
    def setupUi(self, MainDialog):
        MainDialog.setObjectName(_fromUtf8("MainDialog"))
        MainDialog.resize(994, 647)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/plugins/qgis2web/icons/qgis2web.png")),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainDialog.setWindowIcon(icon)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(MainDialog)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.tabWidget = QtWidgets.QTabWidget(MainDialog)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab_export = QtWidgets.QWidget()
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                       QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab_export.setSizePolicy(sizePolicy)
        self.tab_export.setObjectName(_fromUtf8("tab"))
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.tab)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.splitter_2 = QtWidgets.QSplitter(self.tab)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding,
                                       QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(
            self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.layoutWidget = QtWidgets.QWidget(self.splitter_2)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtWidgets.QSplitter(self.layoutWidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layersTree = QtWidgets.QTreeWidget(self.splitter)
        self.layersTree.setMinimumSize(QtCore.QSize(400, 0))
        self.layersTree.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.layersTree.setObjectName(_fromUtf8("layersTree"))
        self.layersTree.headerItem().setText(0, _fromUtf8("1"))
        self.layersTree.header().setVisible(False)
        self.layersTree.header().setDefaultSectionSize(200)
        self.widget = QtWidgets.QWidget(self.splitter)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.appearanceParams = QtWidgets.QTreeWidget(self.widget)
        self.appearanceParams.setMinimumSize(QtCore.QSize(300, 0))
        self.appearanceParams.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.appearanceParams.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.appearanceParams.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarAlwaysOff)
        self.appearanceParams.setAutoScroll(False)
        self.appearanceParams.setObjectName(_fromUtf8("appearanceParams"))
        self.appearanceParams.header().setVisible(False)
        self.appearanceParams.header().setCascadingSectionResizes(False)
        self.appearanceParams.header().setDefaultSectionSize(200)
        self.verticalLayout_5.addWidget(self.appearanceParams)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 6)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtWidgets.QSpacerItem(5, 20, QtWidgets.QSizePolicy.Fixed,
                                       QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.ol3 = QtWidgets.QRadioButton(self.widget)
        self.ol3.setChecked(True)
        self.ol3.setObjectName(_fromUtf8("ol3"))
        self.mapFormat = QtWidgets.QButtonGroup(MainDialog)
        self.mapFormat.setObjectName(_fromUtf8("mapFormat"))
        self.mapFormat.addButton(self.ol3)
        self.horizontalLayout_2.addWidget(self.ol3)
        self.leaflet = QtWidgets.QRadioButton(self.widget)
        self.leaflet.setObjectName(_fromUtf8("leaflet"))
        self.mapFormat.addButton(self.leaflet)
        self.horizontalLayout_2.addWidget(self.leaflet)
        self.buttonPreview = QtWidgets.QPushButton(self.widget)
        self.buttonPreview.setMinimumSize(QtCore.QSize(0, 24))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/plugins/qgis2web/icons/preview.gif")),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonPreview.setIcon(icon1)
        self.buttonPreview.setObjectName(_fromUtf8("buttonPreview"))
        self.horizontalLayout_2.addWidget(self.buttonPreview)
        self.buttonExport = QtWidgets.QPushButton(self.widget)
        self.buttonExport.setIcon(icon)
        self.buttonExport.setObjectName(_fromUtf8("buttonExport"))
        self.horizontalLayout_2.addWidget(self.buttonExport)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.splitter)
        #self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.splitter_2)
        #self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        #self.right_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        #self.right_layout.setMargin(0)
        #self.right_layout.setObjectName(_fromUtf8("right_layout"))
        self.horizontalLayout.addWidget(self.splitter_2)
        self.tabWidget.addTab(self.tab_export, _fromUtf8(""))
        uitime = Ui_TimeDialog(self.tabWidget, MainDialog)
        self.tab_settings = QtWidgets.QWidget()
        self.tab_settings.setObjectName(_fromUtf8("tab_settings"))
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.tab_settings)
        self.verticalLayout_6.setObjectName(_fromUtf8("verticalLayout_6"))
        self.verticalLayout_6.setAlignment(QtCore.Qt.AlignTop)
        self.verticalLayout_6.setContentsMargins(11,16,11,11)
        self.previewOnStartup = QtWidgets.QCheckBox(self.tab_settings)
        self.previewOnStartup.setChecked(True)
        self.previewOnStartup.setObjectName(_fromUtf8("previewOnStartup"))
        self.verticalLayout_6.addWidget(self.previewOnStartup)
        self.closeFeedbackOnSuccess = QtWidgets.QCheckBox(self.tab_settings)
        self.closeFeedbackOnSuccess.setChecked(True)
        self.closeFeedbackOnSuccess.setObjectName(_fromUtf8("closeFeedbackOnSuccess"))
        self.verticalLayout_6.addWidget(self.closeFeedbackOnSuccess)
        self.previewFeatureLimitLabel = QtWidgets.QLabel("Preview feature limit per layer: ", self.tab_settings)
        self.previewFeatureLimit = QtWidgets.QLineEdit(self.tab_settings)
        self.previewFeatureLimit.setObjectName(_fromUtf8("previewFeatureLimit"))
        self.previewFeatureLimit.setFixedWidth(120)
        self.verticalLayout_6.addWidget(self.previewFeatureLimitLabel)
        self.verticalLayout_6.addWidget(self.previewFeatureLimit)
        self.tabWidget.addTab(self.tab_settings, _fromUtf8(""))
        self.tab_help = QtWidgets.QWidget()
        self.tab_help.setStyleSheet(_fromUtf8(
            "background-color: rgb(255, 255, 255);"))
        self.tab_help.setObjectName(_fromUtf8("tab_help"))
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.tab_help)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.helpField = QtWidgets.QTextBrowser(self.tab_help)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.helpField.setFont(font)
        self.helpField.setStyleSheet(_fromUtf8("padding: 10px;"))
        self.helpField.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.helpField.setFrameShadow(QtWidgets.QFrame.Plain)
        self.helpField.setLineWidth(0)
        self.helpField.setObjectName(_fromUtf8("helpField"))
        self.horizontalLayout_4.addWidget(self.helpField)
        self.tabWidget.addTab(self.tab_help, _fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.tabWidget)

        self.retranslateUi(MainDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainDialog)

    def retranslateUi(self, MainDialog):
        MainDialog.setWindowTitle(_translate("MainDialog", "Export to web map",
                                             None))
        self.layersTree.headerItem().setText(1, _translate("MainDialog", "2",
                                             None))
        self.appearanceParams.headerItem().setText(0, _translate("MainDialog",
                                                             "Setting", None))
        self.appearanceParams.headerItem().setText(1, _translate("MainDialog",
                                                             "Value", None))
        self.ol3.setText(_translate("MainDialog", "OpenLayers", None))
        self.leaflet.setText(_translate("MainDialog", "Leaflet", None))
        self.buttonPreview.setText(_translate("MainDialog", "Update preview",
                                              None))
        self.buttonExport.setText(_translate("MainDialog", "Export", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_export),
                                  _translate("MainDialog", "Export", None))
        self.previewOnStartup.setText(_translate("MainDialog",
                                                 "Preview on startup", None))
        self.closeFeedbackOnSuccess.setText(_translate("MainDialog",
                                                 "Close feedback dialog on success", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_settings),
                                  _translate("MainDialog", "Settings", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_help),
                                  _translate("MainDialog", "Help", None))
