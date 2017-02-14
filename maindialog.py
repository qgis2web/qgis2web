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

import sys
from collections import defaultdict, OrderedDict
import webbrowser

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
# noinspection PyUnresolvedReferences
from PyQt4.QtCore import *
from PyQt4.QtCore import (QSettings,
                          QByteArray)
from PyQt4.QtGui import *
from PyQt4.QtGui import (QHBoxLayout)
try:
    from PyQt4.QtWebKit import *
    webkit_available = True
except ImportError:
    webkit_available = False
from PyQt4 import QtGui
import traceback
import logging

from ui_maindialog import Ui_MainDialog
import utils
from configparams import getParams, baselayers, specificParams, specificOptions
from olwriter import writeOL
from leafletWriter import *
from exporter import (EXPORTER_REGISTRY,
                      FolderExporter)

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MainDialog(QDialog, Ui_MainDialog):
    """The main dialog of QGIS2Web plugin."""
    items = {}

    def __init__(self, iface):
        QDialog.__init__(self)
        self.setupUi(self)
        self.iface = iface

        self.previewUrl = None
        self.layer_search_combo = None
        self.exporter_combo = None

        stgs = QSettings()

        self.restoreGeometry(stgs.value("qgis2web/MainDialogGeometry",
                                        QByteArray(), type=QByteArray))

        if stgs.value("qgis2web/previewOnStartup", Qt.Checked) == Qt.Checked:
            self.previewOnStartup.setCheckState(Qt.Checked)
        else:
            self.previewOnStartup.setCheckState(Qt.Unchecked)
        self.paramsTreeOL.setSelectionMode(QAbstractItemView.SingleSelection)
        self.preview = None
        if webkit_available:
            widget = QWebView()
            self.preview = widget
            webview = self.preview.page()
            webview.setNetworkAccessManager(QgsNetworkAccessManager.instance())
            self.preview.settings().setAttribute(
                QWebSettings.DeveloperExtrasEnabled, True)
        else:
            widget = QTextBrowser()
            widget.setText(self.tr('Preview is not available since QtWebKit '
                                   'dependency is missing on your system'))
        self.right_layout.insertWidget(0, widget)
        self.populateConfigParams(self)
        self.populate_layers_and_groups(self)
        self.populateLayerSearch()
        self.populateBasemaps()

        self.exporter = EXPORTER_REGISTRY.createFromProject()
        self.exporter_combo.setCurrentIndex(self.exporter_combo.findText(self.exporter.name()))
        self.exporter_combo.currentIndexChanged.connect(self.exporterTypeChanged)

        self.selectMapFormat()
        self.toggleOptions()
        if webkit_available:
            if self.previewOnStartup.checkState() == Qt.Checked:
                self.previewMap()
            self.buttonPreview.clicked.connect(self.previewMap)
        else:
            self.buttonPreview.setDisabled(True)
        self.layersTree.model().dataChanged.connect(self.populateLayerSearch)
        self.ol3.clicked.connect(self.changeFormat)
        self.leaflet.clicked.connect(self.changeFormat)
        self.buttonExport.clicked.connect(self.saveMap)
        readme = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                              "README.md")
        helpText = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                "helpFile.md")
        lines = open(readme, 'r').readlines()
        with open(helpText, 'w') as helpFile:
            for ct, line in enumerate(lines):
                if ct > 4:
                    helpFile.write(line)
            helpFile.close()
        self.helpField.setSource(QUrl.fromLocalFile(helpText))
        if webkit_available:
            self.devConsole = QWebInspector(self.verticalLayoutWidget_2)
            self.devConsole.setFixedHeight(0)
            self.devConsole.setObjectName("devConsole")
            self.devConsole.setPage(self.preview.page())
            self.right_layout.insertWidget(1, self.devConsole)
        self.filter = devToggleFilter()
        self.installEventFilter(self.filter)
        self.setModal(False)

    def changeFormat(self):
        QgsProject.instance().writeEntry("qgis2web", "mapFormat",
                                         self.mapFormat.checkedButton().text())
        self.previewMap()
        self.toggleOptions()

    def exporterTypeChanged(self):
        new_exporter_name = self.exporter_combo.currentText()
        try:
            self.exporter = [e for e in EXPORTER_REGISTRY.getExporters() if e.name() == new_exporter_name][0]()
        except:
            pass

    def toggleOptions(self):
        for param, value in specificParams.iteritems():
            treeParam = self.paramsTreeOL.findItems(param,
                                                    (Qt.MatchExactly |
                                                     Qt.MatchRecursive))[0]
            if self.mapFormat.checkedButton().text() == "OpenLayers 3":
                if value == "OL3":
                    treeParam.setDisabled(False)
                else:
                    treeParam.setDisabled(True)
            else:
                if value == "OL3":
                    treeParam.setDisabled(True)
                else:
                    treeParam.setDisabled(False)
        for option, value in specificOptions.iteritems():
            treeOptions = self.layersTree.findItems(option,
                                                    (Qt.MatchExactly |
                                                     Qt.MatchRecursive))
            for treeOption in treeOptions:
                if self.mapFormat.checkedButton().text() == "OpenLayers 3":
                    if value == "OL3":
                        treeOption.setDisabled(False)
                    else:
                        treeOption.setDisabled(True)
                else:
                    if value == "OL3":
                        treeOption.setDisabled(True)
                    else:
                        treeOption.setDisabled(False)

    def previewMap(self):
        try:
            if self.mapFormat.checkedButton().text() == "OpenLayers 3":
                self.previewOL3()
            else:
                self.previewLeaflet()
        except Exception as e:
            errorHTML = "<html>"
            errorHTML += "<head></head>"
            errorHTML += "<style>body {font-family: sans-serif;}</style>"
            errorHTML += "<body><h1>Error</h1>"
            errorHTML += "<p>qgis2web produced an error:</p><code>"
            errorHTML += traceback.format_exc().replace("\n", "<br />")
            errorHTML += "</code></body></html>"
            if self.preview:
                self.preview.setHtml(errorHTML)
            print traceback.format_exc()

    def saveMap(self):
        if self.mapFormat.checkedButton().text() == "OpenLayers 3":
            MainDialog.saveOL(self)
        else:
            MainDialog.saveLeaf(self)

    def saveSettings(self, paramItem, col):
        QgsProject.instance().removeEntry("qgis2web",
                                          paramItem.name.replace(" ", ""))
        if isinstance(paramItem._value, bool):
            QgsProject.instance().writeEntry("qgis2web",
                                             paramItem.name.replace(" ", ""),
                                             paramItem.checkState(col))
        else:
            QgsProject.instance().writeEntry("qgis2web",
                                             paramItem.name.replace(" ", ""),
                                             paramItem.text(col))
        if paramItem.name == "Match project CRS":
            baseLayer = self.basemaps
            if paramItem.checkState(col):
                baseLayer.setDisabled(True)
            else:
                baseLayer.setDisabled(False)

    def populate_layers_and_groups(self, dlg):
        """Populate layers on QGIS into our layers and group tree view."""
        root_node = QgsProject.instance().layerTreeRoot()
        tree_groups = []
        tree_layers = root_node.findLayers()
        self.layers_item = QTreeWidgetItem()
        self.layers_item.setText(0, "Layers and Groups")
        self.layersTree.setColumnCount(3)

        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if layer.type() != QgsMapLayer.PluginLayer:
                try:
                    if layer.type() == QgsMapLayer.VectorLayer:
                        testDump = layer.rendererV2().dump()
                    layer_parent = tree_layer.parent()
                    if layer_parent.parent() is None:
                        item = TreeLayerItem(self.iface, layer,
                                             self.layersTree, dlg)
                        self.layers_item.addChild(item)
                    else:
                        if layer_parent not in tree_groups:
                            tree_groups.append(layer_parent)
                except:
                    pass

        for tree_group in tree_groups:
            group_name = tree_group.name()
            group_layers = [
                tree_layer.layer() for tree_layer in tree_group.findLayers()]
            item = TreeGroupItem(group_name, group_layers, self.layersTree)
            self.layers_item.addChild(item)

        self.layersTree.addTopLevelItem(self.layers_item)
        self.layersTree.expandAll()
        self.layersTree.resizeColumnToContents(0)
        self.layersTree.resizeColumnToContents(1)
        for i in xrange(self.layers_item.childCount()):
            item = self.layers_item.child(i)
            if item.checkState(0) != Qt.Checked:
                item.setExpanded(False)

    def populateLayerSearch(self):
        self.layer_search_combo.clear()
        self.layer_search_combo.addItem("None")
        (layers, groups, popup, visible,
         json, cluster) = self.getLayersAndGroups()
        for count, layer in enumerate(layers):
            if layer.type() == layer.VectorLayer:
                options = []
                fields = layer.pendingFields()
                for f in fields:
                    fieldIndex = fields.indexFromName(unicode(f.name()))
                    try:
                        formCnf = layer.editFormConfig()
                        editorWidget = formCnf.widgetType(fieldIndex)
                    except:
                        editorWidget = layer.editorWidgetV2(fieldIndex)
                    if (editorWidget == QgsVectorLayer.Hidden or
                            editorWidget == 'Hidden'):
                        continue
                    options.append(unicode(f.name()))
                for option in options:
                    displayStr = unicode(layer.name() + ": " + option)
                    self.layer_search_combo.insertItem(0, displayStr)
                    sln = utils.safeName(layer.name())
                    self.layer_search_combo.setItemData(self.layer_search_combo.findText(displayStr),
                                            sln + unicode(count))

    def configureExporter(self):
        self.exporter.configure()

    def populateConfigParams(self, dlg):
        self.items = defaultdict(dict)
        tree = dlg.paramsTreeOL

        configure_export_action = QAction('...',self)
        configure_export_action.triggered.connect(self.configureExporter)

        params = getParams(configure_exporter_action=configure_export_action)
        for group, settings in params.iteritems():
            item = QTreeWidgetItem()
            item.setText(0, group)
            for param, value in settings.iteritems():
                subitem = self.create_option_item(tree_widget=tree,
                                                  parent_item=item,
                                                  parameter=param,
                                                  value=value)
                item.addChild(subitem)
                self.items[group][param] = subitem
            self.paramsTreeOL.addTopLevelItem(item)
            item.sortChildren(0, Qt.AscendingOrder)
        self.paramsTreeOL.expandAll()
        self.paramsTreeOL.resizeColumnToContents(0)
        self.paramsTreeOL.resizeColumnToContents(1)
        self.layer_search_combo.removeItem(1)

    def create_option_item(self, tree_widget, parent_item, parameter, value):
        project = QgsProject.instance()
        action = None
        if isinstance(value, dict):
            action = value['action']
            value = value['option']

        if isinstance(value, bool):
            value = project.readBoolEntry("qgis2web",
                                          parameter.replace(" ", ""))[0]
        elif isinstance(value, int):
            if project.readNumEntry(
                    "qgis2web", parameter.replace(" ", ""))[0] != 0:
                value = project.readNumEntry("qgis2web",
                                             parameter.replace(" ", ""))[0]
        elif isinstance(value, tuple):
            if project.readNumEntry("qgis2web",
                                    parameter.replace(" ", ""))[0] != 0:
                comboSelection = project.readNumEntry(
                    "qgis2web", parameter.replace(" ", ""))[0]
            elif parameter == "Max zoom level":
                comboSelection = 27
            else:
                comboSelection = 0
        else:
            if (isinstance(project.readEntry("qgis2web",
                                             parameter.replace(" ", ""))[0], basestring) and
                        project.readEntry("qgis2web",
                                          parameter.replace(" ", ""))[0] != ""):
                value = project.readEntry(
                    "qgis2web", parameter.replace(" ", ""))[0]
        subitem = TreeSettingItem(parent_item, tree_widget,
                                  parameter, value, action)
        if parameter == 'Layer search':
            self.layer_search_combo = subitem.combo
        elif parameter == 'Exporter':
            self.exporter_combo = subitem.combo

        if subitem.combo:
            subitem.combo.setCurrentIndex(comboSelection)

        return subitem

    def populateBasemaps(self):
        multiSelect = QtGui.QAbstractItemView.ExtendedSelection
        self.basemaps.setSelectionMode(multiSelect)
        attrFields = []
        for i in range(len(baselayers)):
            for key in baselayers[i]:
                attrFields.append(key)
        self.basemaps.addItems(attrFields)
        basemaps = QgsProject.instance().readEntry("qgis2web", "Basemaps")[0]
        for basemap in basemaps.split(","):
            try:
                self.basemaps.findItems(basemap,
                                        (Qt.MatchExactly))[0].setSelected(True)
            except:
                pass

    def selectMapFormat(self):
        if QgsProject.instance().readEntry("qgis2web",
                                           "mapFormat")[0] == "Leaflet":
            self.ol3.setChecked(False)
            self.leaflet.setChecked(True)

    def loadPreviewFile(self, file):
        """
        Loads a web based preview from a local file path
        """
        self.previewUrl = QUrl.fromLocalFile(file)
        if self.preview:
            self.preview.settings().clearMemoryCaches()
            self.preview.setUrl(self.previewUrl)

    def previewOL3(self):
        (layers, groups, popup, visible,
         json, cluster) = self.getLayersAndGroups()
        params = self.getParameters()
        previewFile = writeOL(self.iface, layers, groups, popup, visible, json,
                              cluster, params, utils.tempFolder())
        self.loadPreviewFile(previewFile)

    def previewLeaflet(self):
        (layers, groups, popup, visible,
         json, cluster) = self.getLayersAndGroups()
        params = self.getParameters()
        previewFile = writeLeaflet(self.iface, utils.tempFolder(), layers,
                                   visible, cluster, json, params, popup)
        self.loadPreviewFile(previewFile)

    def saveOL(self):
        params = self.getParameters()
        write_folder = self.exporter.exportDirectory()
        if write_folder:
            (layers, groups, popup, visible,
             json, cluster) = self.getLayersAndGroups()
            outputFile = writeOL(self.iface, layers, groups, popup, visible,
                                 json, cluster, params, write_folder)
            self.exporter.postProcess(outputFile)
            if (not os.environ.get('CI') and
                    not os.environ.get('TRAVIS')):
                webbrowser.open_new_tab(self.exporter.destinationUrl())

    def saveLeaf(self):
        params = self.getParameters()
        write_folder = self.exporter.exportDirectory()
        if write_folder:
            (layers, groups, popup, visible,
             json, cluster) = self.getLayersAndGroups()
            outputFile = writeLeaflet(self.iface, write_folder, layers, visible,
                                      cluster, json, params, popup)
            self.exporter.postProcess(outputFile)
            webbrowser.open_new_tab(self.exporter.destinationUrl())

    def getParameters(self):
        parameters = defaultdict(dict)
        for group, settings in self.items.iteritems():
            for param, item in settings.iteritems():
                parameters[group][param] = item.value()
                if param == "Layer search":
                    parameters["Appearance"]["Search layer"] = (
                        self.layer_search_combo.itemData(self.layer_search_combo.currentIndex()))
        basemaps = self.basemaps.selectedItems()
        parameters["Appearance"]["Base layer"] = basemaps
        return parameters

    def saveParameters(self):
        QgsProject.instance().removeEntry("qgis2web", "/")
        parameters = defaultdict(dict)
        for group, settings in self.items.iteritems():
            for param, item in settings.iteritems():
                QgsProject.instance().writeEntry("qgis2web",
                                                 param.replace(" ", ""),
                                                 item.setting())
        EXPORTER_REGISTRY.writeToProject(self.exporter)
        basemaps = self.basemaps.selectedItems()
        basemaplist = ",".join(basemap.text() for basemap in basemaps)
        QgsProject.instance().writeEntry("qgis2web", "Basemaps", basemaplist)
        return parameters

    def getLayersAndGroups(self):
        layers = []
        groups = {}
        popup = []
        visible = []
        json = []
        cluster = []
        for i in xrange(self.layers_item.childCount()):
            item = self.layers_item.child(i)
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
                    if hasattr(item, "json") and item.json:
                        json.append(True)
                    else:
                        json.append(False)
                    if hasattr(item, "cluster") and item.cluster:
                        cluster.append(True)
                    else:
                        cluster.append(False)
                groups[group] = groupLayers[::-1]

        return (layers[::-1],
                groups,
                popup[::-1],
                visible[::-1],
                json[::-1],
                cluster[::-1])

    def closeEvent(self, event):
        self.saveParameters()
        (layers, groups, popup, visible,
         json, cluster) = self.getLayersAndGroups()
        for layer, pop, vis in zip(layers, popup, visible):
            attrDict = {}
            for attr in pop:
                attrDict['attr'] = pop[attr]
                layer.setCustomProperty("qgis2web/popup/" + attr, pop[attr])
                layer.setCustomProperty("qgis2web/Visible", vis)

        QSettings().setValue(
            "qgis2web/MainDialogGeometry", self.saveGeometry())

        QSettings().setValue("qgis2web/previewOnStartup",
                             self.previewOnStartup.checkState())
        event.accept()


class devToggleFilter(QObject):
    devToggle = pyqtSignal()

    def eventFilter(self, obj, event):
        try:
            if event.type() == QEvent.KeyPress:
                if event.key() == Qt.Key_F12:
                    self.devToggle.emit()
                    if obj.devConsole.height() != 0:
                        obj.devConsole.setFixedHeight(0)
                    else:
                        obj.devConsole.setFixedHeight(168)
                    return True
        except:
            pass
        return False


class TreeGroupItem(QTreeWidgetItem):

    groupIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons",
                                   "group.gif"))

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

    layerIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons",
                                   "layer.png"))

    def __init__(self, iface, layer, tree, dlg):
        QTreeWidgetItem.__init__(self)
        self.iface = iface
        self.layer = layer
        self.setText(0, layer.name())
        self.setIcon(0, self.layerIcon)
        project = QgsProject.instance()
        if project.layerTreeRoot().findLayer(layer.id()).isVisible():
            self.setCheckState(0, Qt.Checked)
        else:
            self.setCheckState(0, Qt.Unchecked)
        if layer.type() == layer.VectorLayer:
            self.popupItem = QTreeWidgetItem(self)
            self.popupItem.setText(0, "Popup fields")
            options = []
            fields = self.layer.pendingFields()
            for f in fields:
                fieldIndex = fields.indexFromName(unicode(f.name()))
                try:
                    formCnf = layer.editFormConfig()
                    editorWidget = formCnf.widgetType(fieldIndex)
                except:
                    editorWidget = layer.editorWidgetV2(fieldIndex)
                if (editorWidget == QgsVectorLayer.Hidden or
                        editorWidget == 'Hidden'):
                    continue
                options.append(f.name())
            for option in options:
                self.attr = QTreeWidgetItem(self)
                self.attrWidget = QComboBox()
                self.attrWidget.addItem("no label")
                self.attrWidget.addItem("inline label")
                self.attrWidget.addItem("header label")
                custProp = layer.customProperty("qgis2web/popup/" + option)
                if (custProp != "" and custProp is not None):
                    self.attrWidget.setCurrentIndex(
                        self.attrWidget.findText(
                            layer.customProperty("qgis2web/popup/" + option)))
                self.attr.setText(1, option)
                self.popupItem.addChild(self.attr)
                tree.setItemWidget(self.attr, 2, self.attrWidget)
            self.addChild(self.popupItem)
        self.visibleItem = QTreeWidgetItem(self)
        self.visibleCheck = QCheckBox()
        vis = layer.customProperty("qgis2web/Visible", True)
        if (vis == 0 or unicode(vis).lower() == "false"):
            self.visibleCheck.setChecked(False)
        else:
            self.visibleCheck.setChecked(True)
        self.visibleItem.setText(0, "Visible")
        self.addChild(self.visibleItem)
        tree.setItemWidget(self.visibleItem, 1, self.visibleCheck)
        if layer.type() == layer.VectorLayer:
            if layer.providerType() == 'WFS':
                self.jsonItem = QTreeWidgetItem(self)
                self.jsonCheck = QCheckBox()
                if layer.customProperty("qgis2web/Encode to JSON") == 2:
                    self.jsonCheck.setChecked(True)
                self.jsonItem.setText(0, "Encode to JSON")
                self.jsonCheck.stateChanged.connect(self.changeJSON)
                self.addChild(self.jsonItem)
                tree.setItemWidget(self.jsonItem, 1, self.jsonCheck)
            if layer.geometryType() == QGis.Point:
                self.clusterItem = QTreeWidgetItem(self)
                self.clusterCheck = QCheckBox()
                if layer.customProperty("qgis2web/Cluster") == 2:
                    self.clusterCheck.setChecked(True)
                self.clusterItem.setText(0, "Cluster")
                self.clusterCheck.stateChanged.connect(self.changeCluster)
                self.addChild(self.clusterItem)
                tree.setItemWidget(self.clusterItem, 1, self.clusterCheck)

    @property
    def popup(self):
        popup = []
        self.tree = self.treeWidget()
        for p in xrange(self.childCount()):
            item = self.child(p).text(1)
            if item != "":
                popupVal = self.tree.itemWidget(self.child(p), 2).currentText()
                pair = (item, popupVal)
                popup.append(pair)
        popup = OrderedDict(popup)
        return popup

    @property
    def visible(self):
        return self.visibleCheck.isChecked()

    @property
    def json(self):
        try:
            return self.jsonCheck.isChecked()
        except:
            return False

    @property
    def cluster(self):
        try:
            return self.clusterCheck.isChecked()
        except:
            return False

    def changeJSON(self, isJSON):
        self.layer.setCustomProperty("qgis2web/Encode to JSON", isJSON)

    def changeCluster(self, isCluster):
        self.layer.setCustomProperty("qgis2web/Cluster", isCluster)


class TreeSettingItem(QTreeWidgetItem):

    def __init__(self, parent, tree, name, value, action=None):
        QTreeWidgetItem.__init__(self, parent)
        self.parent = parent
        self.tree = tree
        self.name = name
        self._value = value
        self.combo = None
        self.setText(0, name)
        widget = None

        if isinstance(value, bool):
            if value:
                self.setCheckState(1, Qt.Checked)
            else:
                self.setCheckState(1, Qt.Unchecked)
        elif isinstance(value, tuple):
            self.combo = QComboBox()
            self.combo.setSizeAdjustPolicy(0)
            for option in value:
                self.combo.addItem(option)
            widget = self.combo
        else:
            self.setText(1, unicode(value))

        if action:
            layout = QHBoxLayout()
            layout.setMargin(0)
            if widget:
                layout.addWidget(widget)
            button = QToolButton()
            button.setDefaultAction(action)
            button.setText(action.text())
            layout.addWidget(button)
            layout.addStretch(1)
            widget=QWidget()
            widget.setLayout(layout)

        if widget:
            self.tree.setItemWidget(self, 1, widget)

    def value(self):
        if isinstance(self._value, bool):
            return self.checkState(1) == Qt.Checked
        elif isinstance(self._value, (int, float)):
            return float(self.text(1))
        elif isinstance(self._value, tuple):
            return self.combo.currentText()
        else:
            return self.text(1)

    def setting(self):
        if isinstance(self._value, bool):
            return self.checkState(1) == Qt.Checked
        elif isinstance(self._value, (int, float)):
            return float(self.text(1))
        elif isinstance(self._value, tuple):
            return self.combo.currentIndex()
        else:
            return self.text(1)
