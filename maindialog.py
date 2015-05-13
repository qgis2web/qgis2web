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

import os
from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from ui_maindialog import Ui_MainDialog
import utils
from configparams import paramsOL
from collections import defaultdict
from olwriter import writeOL
from leafletWriter import *
from qgis.utils import iface
import webbrowser
import tempfile


class MainDialog(QDialog, Ui_MainDialog):

    items = {}

    def __init__(self):
        QDialog.__init__(self)
        self.setupUi(self)
        self.populateLayers()
        self.populateConfigParams()
        self.buttonUpdateOL.clicked.connect(self.previewOL3)
        self.buttonUpdateLeaflet.clicked.connect(self.previewLeaflet)
        self.buttonSaveOL.clicked.connect(self.saveOL)
        self.buttonSaveLeaflet.clicked.connect(self.saveLeaf)
        self.connect(self.labelPreview, SIGNAL("linkActivated(QString)"), self.labelLinkClicked)

    def labelLinkClicked(self, url):
        if url == "open":
            webbrowser.open_new_tab(self.tempIndexFile())

    def populateLayers(self):
        skip_type = [2]
        groups = {}
        rels = iface.legendInterface().groupLayerRelationship()
        groupedLayers = {}
        for rel in rels:
            groupName = rel[0]
            if groupName != '':
                groupLayers = rel[1]
                groups[groupName] = []
                for layerid in groupLayers:
                    groups[groupName].append(QgsMapLayerRegistry.instance().mapLayer(layerid))
                    groupedLayers[layerid] = groupName
        self.layersItem = QTreeWidgetItem()
        self.layersItem.setText(0, "Layers and Groups")
        layers = iface.legendInterface().layers()
        for layer in layers:
            if layer.type() not in skip_type:
                if layer.id() not in groupedLayers:
                    item = TreeLayerItem(layer, self.layersTree)
                    self.layersItem.addChild(item)
                else:
                    groupName = groupedLayers[layer.id()]
                    try:
                        groupLayers = groups[groupName]
                    except KeyError:
                        continue
                    item = TreeGroupItem(groupName, groupLayers, self.layersTree)
                    self.layersItem.addChild(item)
                    del groups[groupName]
            else:
                pass

        self.layersTree.addTopLevelItem(self.layersItem)
        self.layersTree.expandAll()

        self.layersTree.resizeColumnToContents(0)
        self.layersTree.resizeColumnToContents(1)

    def populateConfigParams(self):
        self.items = defaultdict(dict)
        for group, settings in paramsOL.iteritems():
            item = QTreeWidgetItem()
            item.setText(0, group)
            for param,value in settings.iteritems():
                subitem = TreeSettingItem(item, self.paramsTreeOL, param, value)
                item.addChild(subitem)
                self.items[group][param] = subitem
            self.paramsTreeOL.addTopLevelItem(item)
            item.sortChildren(0, Qt.AscendingOrder)
        self.paramsTreeOL.expandAll()
        self.paramsTreeOL.resizeColumnToContents(0)
        self.paramsTreeOL.resizeColumnToContents(1)

    def tempIndexFile(self):
        folder = utils.tempFolder()
        url = "file:///"+ os.path.join(folder, "index.html").replace("\\","/")
        return url

    def previewOL3(self):
        self.preview.settings().clearMemoryCaches()
        layers, groups, popup, visible, json, cluster = self.getLayersAndGroups()
        params = self.getParameters()
        print "folder: " + utils.tempFolder()
        previewFile = writeOL(layers, groups, popup, visible, json, cluster, params, utils.tempFolder())
        self.preview.setUrl(QUrl.fromLocalFile(previewFile))
        self.labelPreview.setText('Preview &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href="open">Open in external browser</a>')

    def previewLeaflet(self):
        self.preview.settings().clearMemoryCaches()
        layers, groups, popup, visible, json, cluster = self.getLayersAndGroups()
        params = self.getParameters()
        print "folder: " + utils.tempFolder()
        previewFile = writeLeaflet(utils.tempFolder(), 500, 700, 1, layers, visible, "", cluster, "", "", "", "", "", "", "", "", 0, 0, json, params)
        self.preview.setUrl(QUrl.fromLocalFile(previewFile))
        self.labelPreview.setText('Preview &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <a href="open">Open in external browser</a>')

    def saveOL(self):
        folder = QFileDialog.getExistingDirectory(self, "Save to directory", tempfile.gettempdir(),
                                                 QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks);
        print "folder: " + folder
        if folder:
            layers, groups, popup, visible, json, cluster = self.getLayersAndGroups()
            params = self.getParameters()
            outputFile = writeOL(layers, groups, popup, visible, json, cluster, params, folder)
            webbrowser.open_new_tab(outputFile)

    def saveLeaf(self):
        folder = QFileDialog.getExistingDirectory(self, "Save to directory", tempfile.gettempdir(),
                                                 QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks);
        if folder:
            layers, groups, popup, visible, json, cluster = self.getLayersAndGroups()
            params = self.getParameters()
            outputFile = writeLeaflet(folder, 600, 400, "", layers, visible, "", cluster, "", "", "", "", "", "", "", "", 0, 0, json, params)
            webbrowser.open_new_tab(outputFile)

    def getParameters(self):
        parameters = defaultdict(dict)
        for group, settings in self.items.iteritems():
            for param, item in settings.iteritems():
                parameters[group][param] = item.value()
        return parameters

    def getLayersAndGroups(self):
        layers = []
        groups = {}
        popup = []
        visible = []
        json = []
        cluster = []
        for i in xrange(self.layersItem.childCount()):
            item = self.layersItem.child(i)
            if isinstance(item, TreeLayerItem):
                if item.checkState(0) == Qt.Checked:
                    layers.append(item.layer)
                    popup.append(item.popup)
                    visible.append(item.visible)
                    json.append(item.json)
                    cluster.append(item.cluster)
            else:
                group = item.name
                groupLayers = []
                if item.checkState(0) != Qt.Checked:
                    continue
                for layer in item.layers:
                    groupLayers.append(layer)
                    layers.append(layer)
                    popup.append(utils.NO_POPUP)
                    if item.visible:
                        visible.append(True)
                    else:
                        visible.append(False)
                    if item.json:
                        json.append(True)
                    else:
                        json.append(False)
                    if item.cluster:
                        cluster.append(True)
                    else:
                        cluster.append(False)
                groups[group] = groupLayers[::-1]

        return layers[::-1], groups, popup[::-1], visible[::-1],  json[::-1], cluster[::-1]


class TreeGroupItem(QTreeWidgetItem):

    groupIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "group.gif"))

    def __init__(self, name, layers, tree):
        QTreeWidgetItem.__init__(self)
        self.layers = layers
        self.name = name
        self.setText(0, name)
        self.setIcon(0, self.groupIcon)
        self.setCheckState(0, Qt.Checked)
        self.visibleItem = QTreeWidgetItem(self)
        self.visibleCheck = QCheckBox()
        self.visibleCheck.setChecked(True)
        self.visibleItem.setText(0, "Layers visibility")
        self.addChild(self.visibleItem)
        tree.setItemWidget(self.visibleItem, 1, self.visibleCheck)

    @property
    def visible(self):
        return self.visibleCheck.isChecked()

class TreeLayerItem(QTreeWidgetItem):

    layerIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "layer.png"))

    def __init__(self, layer, tree):
        QTreeWidgetItem.__init__(self)
        self.layer = layer
        self.setText(0, layer.name())
        self.setIcon(0, self.layerIcon)
        if iface.legendInterface().isLayerVisible(layer):
            self.setCheckState(0, Qt.Checked)
        else:
            self.setCheckState(0, Qt.Unchecked)
        if layer.type() == layer.VectorLayer:
            self.popupItem = QTreeWidgetItem(self)
            self.popupItem.setText(0, "Info popup content")
            self.combo = QComboBox()
            options = ["No popup", "Show all attributes"]
            options.extend(["FIELD:" + f.name() for f in self.layer.pendingFields()])
            for option in options:
                self.combo.addItem(option)
            self.addChild(self.popupItem)
            tree.setItemWidget(self.popupItem, 1, self.combo)
        self.visibleItem = QTreeWidgetItem(self)
        self.visibleCheck = QCheckBox()
        self.visibleCheck.setChecked(True)
        self.visibleItem.setText(0, "Visible")
        self.addChild(self.visibleItem)
        tree.setItemWidget(self.visibleItem, 1, self.visibleCheck)
        if layer.type() == layer.VectorLayer:
			self.jsonItem = QTreeWidgetItem(self)
			self.jsonCheck = QCheckBox()
			self.jsonCheck.setChecked(True)
			self.jsonItem.setText(0, "Encode to JSON")
			self.addChild(self.jsonItem)
			tree.setItemWidget(self.jsonItem, 1, self.jsonCheck)
			self.clusterItem = QTreeWidgetItem(self)
			self.clusterCheck = QCheckBox()
			self.clusterCheck.setChecked(False)
			self.clusterItem.setText(0, "Cluster")
			self.addChild(self.clusterItem)
			tree.setItemWidget(self.clusterItem, 1, self.clusterCheck)

    @property
    def popup(self):
        try:
            idx = self.combo.currentIndex()
            popup = idx if idx < 2 else self.combo.currentText()[len("FIELD:"):]
        except:
            popup = utils.NO_POPUP
        return popup

    @property
    def visible(self):
        return self.visibleCheck.isChecked()

    @property
    def json(self):
        return self.jsonCheck.isChecked()

    @property
    def cluster(self):
        return self.clusterCheck.isChecked()


class TreeSettingItem(QTreeWidgetItem):

    def __init__(self, parent, tree, name, value):
        QTreeWidgetItem.__init__(self, parent)
        self.parent = parent
        self.tree = tree
        self.name = name
        self._value = value
        self.setText(0, name)
        if isinstance(value, bool):
            if value:
                self.setCheckState(1, Qt.Checked)
            else:
                self.setCheckState(1, Qt.Unchecked)
        elif isinstance(value, tuple):
            self.combo = QComboBox()
            for option in value:
                self.combo.addItem(option)
            self.tree.setItemWidget(self, 1, self.combo)
        else:
            self.setFlags(self.flags() | Qt.ItemIsEditable)
            self.setText(1, unicode(value))

    def value(self):
        if isinstance(self._value, bool):
            return self.checkState(1) == Qt.Checked
        elif isinstance(self._value, (int,float)):
            return float(self.text(1))
        elif isinstance(self._value, tuple):
            return self.combo.currentText()
        else:
            return self.text(1)