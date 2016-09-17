# -*- coding: utf-8 -*-

# Form implementation generated from reading
# ui file '/home/wha/qgis2webplugin/ui_maindialog.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!
from PyQt4 import QtWebKit
import resources_rc
from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8

    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


class Ui_MainDialog(object):

    def setupUi(self, MainDialog):
        MainDialog.setObjectName(_fromUtf8("MainDialog"))
        MainDialog.resize(994, 647)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/plugins/qgis2web/icons/qgis2web.png")),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainDialog.setWindowIcon(icon)
        self.horizontalLayout_3 = QtGui.QHBoxLayout(MainDialog)
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.tabWidget = QtGui.QTabWidget(MainDialog)
        self.tabWidget.setAutoFillBackground(True)
        self.tabWidget.setObjectName(_fromUtf8("tabWidget"))
        self.tab = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred,
                                       QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.tab.sizePolicy().hasHeightForWidth())
        self.tab.setSizePolicy(sizePolicy)
        self.tab.setObjectName(_fromUtf8("tab"))
        self.gridLayout_2 = QtGui.QGridLayout(self.tab)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.serviceSelector = QtGui.QHBoxLayout()
        self.serviceSelector.setObjectName(_fromUtf8("serviceSelector"))
        self.genJSON = QtGui.QRadioButton(self.tab)
        self.genJSON.setObjectName(_fromUtf8("genJSON"))
        self.serviceSelector.addWidget(self.genJSON)
        self.vecTileServ = QtGui.QRadioButton(self.tab)
        self.vecTileServ.setObjectName(_fromUtf8("vecTileServ"))
        self.serviceSelector.addWidget(self.vecTileServ)
        self.label = QtGui.QLabel(self.tab)
        self.label.setObjectName(_fromUtf8("label"))
        self.serviceSelector.addWidget(self.label)
        self.lineEdit = QtGui.QLineEdit(self.tab)
        self.lineEdit.setObjectName(_fromUtf8("lineEdit"))
        self.serviceSelector.addWidget(self.lineEdit)
        self.gridLayout.addLayout(self.serviceSelector, 0, 0, 1, 1)
        self.splitter_2 = QtGui.QSplitter(self.tab)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.splitter_2.sizePolicy().
                                     hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.layoutWidget = QtGui.QWidget(self.splitter_2)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.layoutWidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layersTree = QtGui.QTreeWidget(self.splitter)
        self.layersTree.setMinimumSize(QtCore.QSize(400, 0))
        self.layersTree.setHorizontalScrollBarPolicy(QtCore.Qt.
                                                     ScrollBarAlwaysOff)
        self.layersTree.setObjectName(_fromUtf8("layersTree"))
        self.layersTree.headerItem().setText(0, _fromUtf8("1"))
        self.layersTree.header().setVisible(False)
        self.layersTree.header().setDefaultSectionSize(200)
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.paramsTreeOL = QtGui.QTreeWidget(self.widget)
        self.paramsTreeOL.setMinimumSize(QtCore.QSize(300, 0))
        self.paramsTreeOL.setFrameShape(QtGui.QFrame.StyledPanel)
        self.paramsTreeOL.setFrameShadow(QtGui.QFrame.Sunken)
        self.paramsTreeOL.setHorizontalScrollBarPolicy(QtCore.Qt.
                                                       ScrollBarAlwaysOff)
        self.paramsTreeOL.setAutoScroll(False)
        self.paramsTreeOL.setObjectName(_fromUtf8("paramsTreeOL"))
        self.paramsTreeOL.header().setVisible(False)
        self.paramsTreeOL.header().setCascadingSectionResizes(False)
        self.paramsTreeOL.header().setDefaultSectionSize(200)
        self.verticalLayout_5.addWidget(self.paramsTreeOL)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, -1, -1, 6)
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        spacerItem = QtGui.QSpacerItem(5, 20, QtGui.QSizePolicy.Fixed,
                                       QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.ol3 = QtGui.QRadioButton(self.widget)
        self.ol3.setChecked(True)
        self.ol3.setObjectName(_fromUtf8("ol3"))
        self.mapFormat = QtGui.QButtonGroup(MainDialog)
        self.mapFormat.setObjectName(_fromUtf8("mapFormat"))
        self.mapFormat.addButton(self.ol3)
        self.horizontalLayout_2.addWidget(self.ol3)
        self.leaflet = QtGui.QRadioButton(self.widget)
        self.leaflet.setObjectName(_fromUtf8("leaflet"))
        self.mapFormat.addButton(self.leaflet)
        self.horizontalLayout_2.addWidget(self.leaflet)
        self.buttonPreview = QtGui.QPushButton(self.widget)
        self.buttonPreview.setMinimumSize(QtCore.QSize(0, 24))
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(_fromUtf8(":/plugins/qgis2web/icons/preview.gif")),
            QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonPreview.setIcon(icon1)
        self.buttonPreview.setObjectName(_fromUtf8("buttonPreview"))
        self.horizontalLayout_2.addWidget(self.buttonPreview)
        self.buttonExport = QtGui.QPushButton(self.widget)
        self.buttonExport.setIcon(icon)
        self.buttonExport.setObjectName(_fromUtf8("buttonExport"))
        self.horizontalLayout_2.addWidget(self.buttonExport)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.splitter)
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.splitter_2)
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("\
                                                  verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.preview = QtWebKit.QWebView(self.verticalLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding,
                                       QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.preview.sizePolicy().
                                     hasHeightForWidth())
        self.preview.setSizePolicy(sizePolicy)
        self.preview.setProperty("url", QtCore.QUrl(_fromUtf8("about:blank")))
        self.preview.setObjectName(_fromUtf8("preview"))
        self.verticalLayout_2.addWidget(self.preview)
        self.basemaps = QtGui.QListWidget(self.verticalLayoutWidget_2)
        self.basemaps.setObjectName(_fromUtf8("basemaps"))
        self.verticalLayout_2.addWidget(self.basemaps)
        self.gridLayout.addWidget(self.splitter_2, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        self.tabWidget.addTab(self.tab, _fromUtf8(""))
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setStyleSheet(_fromUtf8("\
                                 background-color: rgb(255, 255, 255);"))
        self.tab_2.setObjectName(_fromUtf8("tab_2"))
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.tab_2)
        self.horizontalLayout_4.setObjectName(_fromUtf8("horizontalLayout_4"))
        self.helpField = QtGui.QTextBrowser(self.tab_2)
        font = QtGui.QFont()
        font.setPointSize(11)
        self.helpField.setFont(font)
        self.helpField.setStyleSheet(_fromUtf8("padding: 10px;"))
        self.helpField.setFrameShape(QtGui.QFrame.NoFrame)
        self.helpField.setFrameShadow(QtGui.QFrame.Plain)
        self.helpField.setLineWidth(0)
        self.helpField.setObjectName(_fromUtf8("helpField"))
        self.horizontalLayout_4.addWidget(self.helpField)
        self.tabWidget.addTab(self.tab_2, _fromUtf8(""))
        self.horizontalLayout_3.addWidget(self.tabWidget)

        self.retranslateUi(MainDialog)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainDialog)

    def retranslateUi(self, MainDialog):
        MainDialog.setWindowTitle(_translate("MainDialog", "Export to web map",
                                             None))
        self.genJSON.setText(_translate("MainDialog", "Generate JSON",
                                        None))
        self.vecTileServ.setText(_translate("MainDialog",
                                            "Vector Tile Service", None))
        self.label.setText(_translate("MainDialog", "Url:", None))
        self.layersTree.headerItem().setText(1, _translate("MainDialog", "2",
                                             None))
        self.paramsTreeOL.headerItem().setText(0, _translate("MainDialog",
                                                             "Setting", None))
        self.paramsTreeOL.headerItem().setText(1, _translate("MainDialog",
                                                             "Value", None))
        self.ol3.setText(_translate("MainDialog", "OpenLayers 3", None))
        self.leaflet.setText(_translate("MainDialog", "Leaflet", None))
        self.buttonPreview.setText(_translate("MainDialog", "Update preview",
                                              None))
        self.buttonExport.setText(_translate("MainDialog", "Export", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab), _translate("MainDialog", "Export", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(
            self.tab_2), _translate("MainDialog", "Help", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainDialog = QtGui.QDialog()
    ui = Ui_MainDialog()
    ui.setupUi(MainDialog)
    MainDialog.show()
    sys.exit(app.exec_())
