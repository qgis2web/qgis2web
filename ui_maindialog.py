# -*- coding: utf-8 -*-

# qgis-ol3 Creates OpenLayers map from QGIS layers
# Copyright (C) 2014 Victor Olaya (volayaf@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# Form implementation generated from reading ui file 'ui_maindialog.ui'
#
# Created: Thu Jun 19 10:23:10 2014
#      by: PyQt4 UI code generator 4.11
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui, QtWebKit
import resources_rc

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
        MainDialog.resize(994, 736)
        icon = QtGui.QIcon(QtGui.QApplication)
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/qgis2web/icons/qgis2web.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iconOL = QtGui.QIcon(QtGui.QApplication)
        iconOL.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/qgis2web/icons/ol.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        iconLeaf = QtGui.QIcon(QtGui.QApplication)
        iconLeaf.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/qgis2web/icons/leaflet.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainDialog.setWindowIcon(icon)
        self.verticalLayout_3 = QtGui.QVBoxLayout(MainDialog)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter_2 = QtGui.QSplitter(MainDialog)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.layoutWidget = QtGui.QWidget(self.splitter_2)
        self.layoutWidget.setObjectName(_fromUtf8("layoutWidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setMargin(0)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.label = QtGui.QLabel(self.layoutWidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout.addWidget(self.label)
        self.splitter = QtGui.QSplitter(self.layoutWidget)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.layersTree = QtGui.QTreeWidget(self.splitter)
        self.layersTree.setMinimumSize(QtCore.QSize(400, 300))
        self.layersTree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.layersTree.setObjectName(_fromUtf8("layersTree"))
        self.layersTree.headerItem().setText(0, _fromUtf8("1"))
        self.layersTree.header().setVisible(False)
        self.layersTree.header().setDefaultSectionSize(200)
        self.widget = QtGui.QWidget(self.splitter)
        self.widget.setMinimumSize(QtCore.QSize(0, 0))
        self.widget.setObjectName(_fromUtf8("widget"))
        self.verticalLayout_5 = QtGui.QVBoxLayout(self.widget)
        self.verticalLayout_5.setSpacing(6)
        self.verticalLayout_5.setMargin(0)
        self.verticalLayout_5.setObjectName(_fromUtf8("verticalLayout_5"))
        self.label_3 = QtGui.QLabel(self.widget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.verticalLayout_5.addWidget(self.label_3)
        self.paramsTreeOL = QtGui.QTreeWidget(self.widget)
        self.paramsTreeOL.setMinimumSize(QtCore.QSize(300, 0))
        self.paramsTreeOL.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.paramsTreeOL.setFrameShape(QtGui.QFrame.StyledPanel)
        self.paramsTreeOL.setFrameShadow(QtGui.QFrame.Sunken)
        self.paramsTreeOL.setObjectName(_fromUtf8("paramsTreeOL"))
        self.paramsTreeOL.header().setVisible(True)
        self.paramsTreeOL.header().setCascadingSectionResizes(False)
        self.paramsTreeOL.header().setDefaultSectionSize(200)
        self.verticalLayout_5.addWidget(self.paramsTreeOL)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.buttonSaveOL = QtGui.QPushButton(self.widget)
        self.buttonSaveOL.setIcon(iconOL)
        self.buttonSaveOL.setObjectName(_fromUtf8("buttonSaveOL"))
        self.horizontalLayout_2.addWidget(self.buttonSaveOL)
        self.buttonSaveLeaflet = QtGui.QPushButton(self.widget)
        self.buttonSaveLeaflet.setIcon(iconLeaf)
        self.buttonSaveLeaflet.setObjectName(_fromUtf8("buttonSaveLeaflet"))
        self.horizontalLayout_2.addWidget(self.buttonSaveLeaflet)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.buttonUpdateOL = QtGui.QPushButton(self.widget)
        icon1 = QtGui.QIcon(QtGui.QApplication)
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/plugins/qgis2web/icons/preview.gif")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonUpdateOL.setIcon(icon1)
        self.buttonUpdateOL.setObjectName(_fromUtf8("buttonUpdateOL"))
        self.horizontalLayout_2.addWidget(self.buttonUpdateOL)
        self.buttonUpdateLeaflet = QtGui.QPushButton(self.widget)
        self.buttonUpdateLeaflet.setIcon(icon1)
        self.buttonUpdateLeaflet.setObjectName(_fromUtf8("buttonUpdateLeaflet"))
        self.horizontalLayout_2.addWidget(self.buttonUpdateLeaflet)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.splitter)
        self.verticalLayoutWidget_2 = QtGui.QWidget(self.splitter_2)
        self.verticalLayoutWidget_2.setObjectName(_fromUtf8("verticalLayoutWidget_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setMargin(0)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.labelPreview = QtGui.QLabel(self.verticalLayoutWidget_2)
        self.labelPreview.setObjectName(_fromUtf8("labelPreview"))
        self.verticalLayout_2.addWidget(self.labelPreview)
        self.preview = QtWebKit.QWebView(self.verticalLayoutWidget_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.preview.sizePolicy().hasHeightForWidth())
        self.preview.setSizePolicy(sizePolicy)
        self.preview.setUrl(QtCore.QUrl(_fromUtf8("about:blank")))
        self.preview.setObjectName(_fromUtf8("preview"))
        self.verticalLayout_2.addWidget(self.preview)
        self.verticalLayout_3.addWidget(self.splitter_2)

        self.retranslateUi(MainDialog)
        QtCore.QMetaObject.connectSlotsByName(MainDialog)

    def retranslateUi(self, MainDialog):
        MainDialog.setWindowTitle(_translate("MainDialog", "Export to web map", None))
        self.label.setText(_translate("MainDialog", "Layers:", None))
        self.layersTree.headerItem().setText(1, _translate("MainDialog", "2", None))
        self.label_3.setText(_translate("MainDialog", "Settings:", None))
        self.paramsTreeOL.headerItem().setText(0, _translate("MainDialog", "Setting", None))
        self.paramsTreeOL.headerItem().setText(1, _translate("MainDialog", "Value", None))
        self.buttonSaveOL.setText(_translate("MainDialog", "Export OL3", None))
        self.buttonSaveLeaflet.setText(_translate("MainDialog", "Export Leaflet", None))
        self.buttonUpdateOL.setText(_translate("MainDialog", "Preview OL3", None))
        self.buttonUpdateLeaflet.setText(_translate("MainDialog", "Preview Leaflet", None))
        self.labelPreview.setText(_translate("MainDialog", "Preview", None))
