from PyQt5 import QtCore, QtGui, QtWidgets, QtWebKit
import sys
from collections import defaultdict
import qgis  
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebKit import *
from . import utils
import os.path
from qgis.core import *

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

selectedLineedit = "None"
selectedCombo = "None"
selectedLayerCombo = "None"
projectInstance = QgsProject.instance()

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

class Ui_TimeDialog(object):
    def __init__(self, tabWidget, MainDialog):
    ## def setupUi(self, tabWidget, MainDialog):
        self.maindialog = MainDialog
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName(_fromUtf8("tab_3"))
        self.tab3_Layout = QtWidgets.QVBoxLayout(self.tab_3)
        self.tab3_Layout.setObjectName(_fromUtf8("tab3_Layout"))
        
        self.layersTree = QtWidgets.QTreeWidget(self.tab_3)
        self.tab3_Layout.addWidget(self.layersTree)
        self.layersTree.setMinimumSize(QtCore.QSize(400, 0))
        self.layersTree.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.layersTree.setObjectName(_fromUtf8("layersTree"))
        self.layersTree.headerItem().setText(0, _fromUtf8("1"))
        self.layersTree.header().setVisible(False)
        self.layersTree.header().setDefaultSectionSize(200)
        self.layersTree.headerItem().setText(1, _translate("MainDialog", "Layers", None))

        self.populate_layers_and_groups(self)

        self.btn = Button(tabWidget, self)
        self.tab3_Layout.addWidget(self.btn)

        tabWidget.addTab(self.tab_3, _fromUtf8(""))
        tabWidget.setTabText(tabWidget.indexOf(self.tab_3), _translate("MainDialog", "Time", None))

    def populate_layers_and_groups(self, dlg):
        """Populate layers on QGIS into our layers and group tree view."""
        root_node = QgsProject.instance().layerTreeRoot()
        tree_groups = []
        tree_layers = root_node.findLayers()
        ## self.action_item = QTreeWidgetItem()
        ## self.action_item.setText(0, "Add Time")
        ## actionitem = TreeActionItem(self.layersTree)
        ## self.action_item.addChild(actionitem)
        self.layers_item = QTreeWidgetItem()
        self.layers_item.setText(0, "Layers and Groups")

        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            #print "Tree: " + layer.name()
            if layer.type() != QgsMapLayer.PluginLayer:
                try:
                    if layer.type() == QgsMapLayer.VectorLayer:
                        testDump = layer.renderer().dump()
                    layer_parent = tree_layer.parent()
                    # print "Vector: " + layer.name()
                    if layer_parent.parent() is None:
                        item = TreeLayerItem2(layer, self.layersTree, dlg)
                        self.layers_item.addChild(item)
                    else:
                        if layer_parent not in tree_groups:
                            tree_groups.append(layer_parent)
                except:
                    # print "Except: " + layer.name()
                    # print "Unexpected error:", sys.exc_info()[0]
                    # raise
                    pass

        for tree_group in tree_groups:
            group_name = tree_group.name()
            group_layers = [
                tree_layer.layer() for tree_layer in tree_group.findLayers()]
            item = TreeGroupItem2(group_name, group_layers, self.layersTree)
            self.layers_item.addChild(item)

        self.layersTree.addTopLevelItem(self.layers_item)
        self.layersTree.expandAll()
        self.layersTree.resizeColumnToContents(0)
        self.layersTree.resizeColumnToContents(1)
        for i in range(self.layers_item.childCount()):
            item = self.layers_item.child(i)
            if item.checkState(0) != Qt.Checked:
                item.setExpanded(False)

class TreeGroupItem2(QTreeWidgetItem):

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

class TreeLayerItem2(QTreeWidgetItem):

    layerIcon = QIcon(os.path.join(os.path.dirname(__file__), "icons", "layer.png"))

    def __init__(self, layer, tree, dlg):
        global projectInstance
        #print "Item: " + layer.name()
        QTreeWidgetItem.__init__(self)
        #self.iface = iface
        self.layer = layer
        self.setText(0, layer.name())
        self.setIcon(0, self.layerIcon)
        if projectInstance.layerTreeRoot().findLayer(layer.id()).isVisible():
            self.setCheckState(0, Qt.Checked)
        else:
            self.setCheckState(0, Qt.Unchecked)
        if layer.type() == layer.VectorLayer:
            #TODO
            #Remove no int or string fields or later handle other types
            self.timeFromItem = QTreeWidgetItem(self)
            self.timeFromItem.setText(0, "Time from")
            self.timeFromCombo = QComboBox()
            timeFromOptions = ["No time"]
            for f in self.layer.pendingFields():
                timeFromOptions.append("FIELD:" + f.name())
            for option in timeFromOptions:
                self.timeFromCombo.addItem(option)
            self.addChild(self.timeFromItem)
            if layer.customProperty("qgis2web/Time from"):
                self.timeFromCombo.setCurrentIndex(int(
                    layer.customProperty("qgis2web/Time from")))
            self.timeFromCombo.highlighted.connect(self.clickCombo)
            self.timeFromCombo.currentIndexChanged.connect(self.saveLayerTimeFromComboSettings)
            tree.setItemWidget(self.timeFromItem, 1, self.timeFromCombo)

            self.timeToItem = QTreeWidgetItem(self)
            self.timeToItem.setText(0, "Time to")
            self.timeToCombo = QComboBox()
            timeToOptions = ["No time"]
            for f in self.layer.pendingFields():
                timeToOptions.append("FIELD:" + f.name())
            for option in timeToOptions:
                self.timeToCombo.addItem(option)
            self.addChild(self.timeToItem)
            if layer.customProperty("qgis2web/Time to"):
                self.timeToCombo.setCurrentIndex(int(
                    layer.customProperty("qgis2web/Time to")))
            self.timeToCombo.highlighted.connect(self.clickCombo)
            self.timeToCombo.currentIndexChanged.connect(self.saveLayerTimeToComboSettings)
            tree.setItemWidget(self.timeToItem, 1, self.timeToCombo)
            self.populateMinMax()

    @property
    def timefrom(self):
        try:
            idx = self.timeFromCombo.currentIndex()
            #print """IDX: """ + str(idx)
            if idx < 1:
                timefrom = idx
            else:
                timefrom = self.timeFromCombo.currentText()[len("FIELD:"):]
        except:
            #print "Unexpected error:", sys.exc_info()[1]
            timefrom = utils.NO_TIME
        #print str(timefrom)
        return timefrom

    @property
    def timeto(self):
        try:
            idx = self.timeToCombo.currentIndex()
            #print """IDX: """ + str(idx)
            if idx < 1:
                timeto = idx
            else:
                timeto = self.timeToCombo.currentText()[len("FIELD:"):]
        except:
            #print "Unexpected error:", sys.exc_info()[1]
            timeto = utils.NO_TIME
        #print str(timefrom)
        return timeto

    def clickCombo(self):
        global selectedLayerCombo
        # print self.layer.name()
        selectedLayerCombo = self.layer
        
    def saveLayerTimeFromComboSettings(self, value):
        global selectedLayerCombo
        if selectedLayerCombo != "None":
            selectedLayerCombo.setCustomProperty("qgis2web/Time from", value)
            self.populateMinMax()

    def saveLayerTimeToComboSettings(self, value):
        global selectedLayerCombo
        if selectedLayerCombo != "None":
            selectedLayerCombo.setCustomProperty("qgis2web/Time to", value)
            self.populateMinMax()
            
    #ruzicka
    #TODO
    def dateToInt(self, datestr):
        datestr = datestr.replace("-", "")
        if datestr == "NULL":
            datestr = "1000" #TODO work better with null dates
        if len(datestr) == 4:
            datestr = datestr + "0101"
        if len(datestr) == 6:
            datestr = datestr + "01"
        return int(datestr)

    def dateIntToString(self, dateint):
        datestr = str(dateint)
        dateout = datestr[0:4] + "-" + datestr[4:6] + "-" + datestr[6:8]
        return dateout

    def populateMinMax(self):
        global projectInstance
        min = sys.maxsize;
        max = 0;
        root_node = QgsProject.instance().layerTreeRoot()
        tree_layers = root_node.findLayers()
        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.customProperty("qgis2web/Time from") is not None and layer.customProperty("qgis2web/Time to") is not None and layer.customProperty("qgis2web/Time from") is not QPyNullVariant and layer.customProperty("qgis2web/Time to") is not QPyNullVariant:
                    for feat in layer.getFeatures():
                        attrs = feat.attributes()
                        attr = self.dateToInt(str(attrs[int(layer.customProperty("qgis2web/Time from")) - 1]))
                        if attr < min:
                            min = attr
                        attr2 = self.dateToInt(str(attrs[int(layer.customProperty("qgis2web/Time to")) - 1]))
                        if attr2 > max:
                            max = attr2
        projectInstance.writeEntry("qgis2web", "Min", self.dateIntToString(min))
        projectInstance.writeEntry("qgis2web", "Max", self.dateIntToString(max))
        #print min
        #print max
        #TODO add text boxes
        ## self.items["Time axis"]["Min"].lineedit.setText(str(min))
        ## self.items["Time axis"]["Max"].lineedit.setText(str(max))

class Button(QPushButton):
    def __init__(self, parent, main):
        super(Button, self).__init__(parent)
        self.main = main
        self.setAcceptDrops(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(
                _fromUtf8(":/plugins/qgis2web/icons/qgis2web.png")),
                QtGui.QIcon.Normal,
                QtGui.QIcon.Off)
        self.setGeometry(QtCore.QRect(90, 90, 61, 51))
        self.setIcon(icon)
        self.setText(_translate("MainDialog", "Add Time", None))
        self.clicked.connect(self.saveMap) #connect here!
        
    def saveMap(self):
        #if projectInstance.readEntry("qgis2web", "mapFormat")[0] == "leaflet":
        #    self.saveLeafletMap()
        #else:
        #    self.saveOLMap()
        if self.main.maindialog.ol3.isChecked():
            self.saveOLMap()
        else:
            self.saveLeafletMap()
        QMessageBox.information(None, "INFO", "Time options were added to index_time.html file.") 
        
    def saveLeafletMap(self):
        # print "Save leaflet"
        dir = projectInstance.readEntry("qgis2web", "Exportfolder")[0]
        # print dir
        root, dirs, files = os.walk(dir).next()
        latest_subdir = max((os.path.getctime(os.path.join(root, f)), f) for f in dirs)
        index = os.path.join(dir, latest_subdir[1], 'index.html')
        html = open(index, 'r').read()
        html = self.addLeafletHeader(html)
        html = self.changeLeafletStyles(html)
        index_time = os.path.join(dir, latest_subdir[1], 'index_time.html')
        f = open(index_time, 'w')
        f.write(html)
        f.close()
    def addLeafletHeader(self, html):
        mintime = projectInstance.readEntry("qgis2web", "Min")[0]
        maxtime = projectInstance.readEntry("qgis2web", "Max")[0]
        
        header = '<script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>\n'
        header += '<link rel="stylesheet" href="https://code.jquery.com/ui/1.10.2/themes/smoothness/jquery-ui.css" />\n'
        header += '<script src="https://code.jquery.com/ui/1.10.2/jquery-ui.js"></script>\n'
        header += '<div style="position: fixed; top: 10px; left: 70px;"><div id="slider-range" style="width:300px"></div>\n'
        header += '<p><input id="datefrom"/>   <input id="dateto"/> </p>\n'
        header += '</div>\n'
        
        header += "<script>\n"
        header += "function getDateString(d) {\n"
        header += "m = d.getMonth() + 1;\n"
        header += "month = String('0' + m).slice(-2);\n"
        header += "day = String('0' + d.getDate()).slice(-2);\n"
        header += "return d.getFullYear() + '-' + month + '-' + day;\n"
        header += "}\n"
        header += "$(document).ready(function() {\n"
        header += "$( '#slider-range' ).slider({\n"
        header += "range: true,\n"
        header += "min: new Date('" + mintime + "').getTime() / 1000,\n"
        header += "max: new Date('" + maxtime + "').getTime() / 1000,\n"
        header += "step: 86400,\n"
        header += "values: [ new Date('" + mintime + "').getTime() / 1000, new Date('" + maxtime + "').getTime() / 1000 ],\n"
        header += "slide: function( event, ui ) {\n"
        header += "var from = new Date(ui.values[0] *1000);\n"
        header += "var to = new Date(ui.values[1] *1000);\n"
        header += "$( '#datefrom' ).val(getDateString(new Date(ui.values[0] *1000)));\n"
        header += "$( '#dateto' ).val(getDateString(new Date(ui.values[1] *1000)));\n"
        header += "setVisibility();\n"
        header += "}\n"
        header += "});\n"
        
        header += "var from = new Date($('#slider-range').slider('values', 0)*1000);\n"
        header += "var to = new Date($('#slider-range').slider('values', 1)*1000);\n"
        header += "$( '#datefrom' ).val(getDateString(from));\n"
        header += "$( '#dateto' ).val(getDateString(to));\n"
        header += "});\n"
        
        html = html.replace("<script>", header)
        return html

    def changeLeafletStyles(self, html):
        root_node = QgsProject.instance().layerTreeRoot()
        tree_layers = root_node.findLayers()
        layerid = len(tree_layers) - 1
        layernames = []
        layers = []
        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.customProperty("qgis2web/Time from") is not None and layer.customProperty("qgis2web/Time to") is not None and layer.customProperty("qgis2web/Time from") is not QPyNullVariant and layer.customProperty("qgis2web/Time to") is not QPyNullVariant:
                    start = html.find("function style_" + layer.name())
                    flen = len("function style_") + len(layer.name())
                    layeridstr = html[start+flen:start+flen+2]
                    layernames.append(layer.name() + layeridstr)
                    start2 = html.find("{", start + 1)
                    end = html.find("}", start + 1)
                    style = html[start2+1:end]
                    style = style.replace("return", "s = ") + "\n};"
                    end = html.find("}", end + 1)
                    style = "function style_" + layer.name() + layeridstr + "_0(feature) {" + "\n" + style
                    #print layer.customProperty("qgis2web/Time from")
                    field_from = layer.pendingFields()[int(layer.customProperty("qgis2web/Time from"))-1].name()
                    field_to = layer.pendingFields()[int(layer.customProperty("qgis2web/Time to"))-1].name()
                    
                    style += "var featuredatefrom = String(feature.properties." + field_from + ");\n"
                    style += "var featuredateto = String(feature.properties." + field_to + ");\n"
                    style += "if (featuredatefrom.length == 4) { featuredatefrom = featuredatefrom + '-01-01'; }\n"
                    style += "if (featuredatefrom.length == 7) { featuredatefrom = featuredatefrom + '-01'; }\n"
                    style += "if (featuredateto.length == 4) { featuredateto = featuredateto + '-01-01'; }\n"
                    style += "if (featuredateto.length == 7) { featuredateto = featuredateto + '-01'; }\n"
                    style += "if (\n"
                    style += "(featuredatefrom <= $('#datefrom').val() && featuredateto <= $('#datefrom').val())\n"
                    style += "||\n"
                    style += "(featuredatefrom >= $('#dateto').val() && featuredateto >= $('#dateto').val())\n"
                    style += ") {\n"
                    style += "s['opacity'] = 0.0;\n"
                    style += "s['fillOpacity'] = 0.0;\n"
                    style += "}\n"

                    style += "return s;\n"
                    style += "}\n"
                    
                    style += "function setVisibility" + layer.name() + layeridstr + "() {\n"   
                    style += "for (var row=0; row<1000; row++) {\n"
                    style += "if ( typeof(layer_" + layer.name() + layeridstr + "._layers[row])=='undefined') continue;\n"
                    style += "  s = style_" + layer.name() + layeridstr + "_0(layer_" + layer.name() + layeridstr + "._layers[row].feature);\n"
                    style += "  layer_" + layer.name() + layeridstr + "._layers[row].setStyle(s);\n"
                    style += " }\n"      
                    style += "}\n"
                    html = html[:start] + style + html[end+1:]
                    start = html.find("function doPointToLayer" + layer.name())
                    if start != -1:                  
                        start = html.find("(", start + 1)
                        start = html.find("(", start + 1) 
                        start = html.find("(", start + 1)  
                        html = html[:start] + "(feature" + html[start+1:]        
                layerid -= 1
        fvisibility = "function setVisibility() {\n"
        for layername in layernames:
            fvisibility += "setVisibility" + layername + "();\n"
        fvisibility += "}\n"
        html = html.replace("setBounds();", fvisibility + "setBounds();")
        return html
    
    def saveOLMap(self):
        # print "Save OL"
        dir = projectInstance.readEntry("qgis2web", "Exportfolder")[0]
        if dir == "":
            if os.path.isdir("/tmp/qgis2web"):
                dir = "/tmp/qgis2web"
            if os.path.isdir("C:\\TEMP\\qgis2web"):
                dir = "C:\\TEMP\\qgis2web"
        # print dir
        root, dirs, files = next(os.walk(dir))
        latest_subdir = max((os.path.getctime(os.path.join(root, f)), f) for f in dirs)
        
        index = os.path.join(dir, latest_subdir[1], 'index.html')
        html = open(index, 'r').read()
        
        layernames = self.changeOLStyles(os.path.join(dir, latest_subdir[1], 'styles'))
        
        fvisibility = "function setVisibility() {\n"
        for layername in layernames:
            fvisibility += "lyr_" + layername + ".getSource().changed();\n"
        fvisibility += "}</script>\n"
        
        html = html.replace("_style.js", "_style_time.js")
        
        mintime = projectInstance.readEntry("qgis2web", "Min")[0]
        maxtime = projectInstance.readEntry("qgis2web", "Max")[0]        
        header = '<head>\n<script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>\n'
        header += '<script>\n'
        
        header += "function getDateString(d) {\n"
        header += "m = d.getMonth() + 1;\n"
        header += "month = String('0' + m).slice(-2);\n"
        header += "day = String('0' + d.getDate()).slice(-2);\n"
        header += "return d.getFullYear() + '-' + month + '-' + day;\n"
        header += "}\n"

        header += "$(document).ready(function() {\n"
        header += "$( '#slider-range' ).slider({\n"
        header += "range: true,\n"
        header += "min: new Date('" + mintime + "').getTime() / 1000,\n"
        header += "max: new Date('" + maxtime + "').getTime() / 1000,\n"
        header += "step: 86400,\n"
        header += "values: [ new Date('" + mintime + "').getTime() / 1000, new Date('" + maxtime + "').getTime() / 1000 ],\n"
        header += "slide: function( event, ui ) {\n"
        header += "var from = new Date(ui.values[0] *1000);\n"
        header += "var to = new Date(ui.values[1] *1000);\n"
        header += "$( '#datefrom' ).val(getDateString(new Date(ui.values[0] *1000)));\n"
        header += "$( '#dateto' ).val(getDateString(new Date(ui.values[1] *1000)));\n"
        header += "setVisibility();\n"
        header += "}\n"
        header += "});\n"
        header += "var from = new Date($('#slider-range').slider('values', 0)*1000);\n"
        header += "var to = new Date($('#slider-range').slider('values', 1)*1000);\n"
        header += "$( '#datefrom' ).val(getDateString(from));\n"
        header += "$( '#dateto' ).val(getDateString(to));\n"
        header += "});\n"
        
        header += fvisibility
        html = html.replace("<head>", header)
        
        header = '<link rel="stylesheet" href="https://code.jquery.com/ui/1.10.2/themes/smoothness/jquery-ui.css" />\n'
        header += '<script src="https://code.jquery.com/ui/1.10.2/jquery-ui.js"></script>\n'
        header += '<div style="position: fixed; top: 10px; left: 70px;"><div id="slider-range" style="width:300px"></div>\n'
        header += '<p><input id="datefrom"/>   <input id="dateto"/> </p>\n'
        header += '</div>\n'
        #header = '<p style="position: fixed; top: 0; right: 0;">Time axis: <input type="range" id="date" min="' + mintime + '" max="' + maxtime + '"/><input id="datetxt"/></p></body>'
        html = html.replace("</body>", header)
        
        index_time = os.path.join(dir, latest_subdir[1], 'index_time.html')
        f = open(index_time, 'w')
        f.write(html)
        f.close()
    
    def changeOLStyles(self, path):
        root_node = QgsProject.instance().layerTreeRoot()
        tree_layers = root_node.findLayers()
        layerid = len(tree_layers) - 1
        layernames = []
	#for count, (tree_layer) in enumerate(zip(tree_layers)):
        #sln = safeName(layer.name()) + unicode(count)
        #count = 0
        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if layer.type() == QgsMapLayer.VectorLayer:
                if layer.customProperty("qgis2web/Time from") is not None and layer.customProperty("qgis2web/Time to") is not None and layer.customProperty("qgis2web/Time from") is not QPyNullVariant and layer.customProperty("qgis2web/Time to") is not QPyNullVariant:
                    stylefile = os.path.join(path, layer.name() + unicode(layerid) + "_style.js")
                    styletimefile = os.path.join(path, layer.name() + unicode(layerid) + "_style_time.js")
                    if not os.path.exists(stylefile):
                        stylefile = os.path.join(path, layer.name() + "_style.js")
                        styletimefile = os.path.join(path, layer.name() + "_style_time.js")
                    else:
                        layernames.append(layer.name() + unicode(layerid))
                    if not os.path.exists(stylefile):
                        stylefile = os.path.join(path, layer.name() + "_" + unicode(layerid) + "_style.js")
                        styletimefile = os.path.join(path, layer.name() + "_" + unicode(layerid) + "_style_time.js")
                        layernames.append(layer.name() +  "_" + unicode(layerid))
                    else:
                        layernames.append(layer.name())
                    style = open(stylefile, 'r').read()
                    start = style.find("var style =")
                    end = style.find(";", start)
                    styledef = style[start+4:end+1]
                    field_from = layer.pendingFields()[int(layer.customProperty("qgis2web/Time from"))-1].name()
                    field_to = layer.pendingFields()[int(layer.customProperty("qgis2web/Time to"))-1].name()
                    stylevis = "var featuredatefrom = String(feature.get('" + field_from + "'));\n"
                    stylevis += "var featuredateto = String(feature.get('" + field_to + "'));\n"
                    stylevis += "if (featuredatefrom.length == 4) { featuredatefrom = featuredatefrom + '-01-01'; }\n"
                    stylevis += "if (featuredatefrom.length == 7) { featuredatefrom = featuredatefrom + '-01'; }\n"
                    stylevis += "if (featuredateto.length == 4) { featuredateto = featuredateto + '-01-01'; }\n"
                    stylevis += "if (featuredateto.length == 7) { featuredateto = featuredateto + '-01'; }\n"
                    stylevis += "if (\n"
                    stylevis += "(featuredatefrom <= $('#datefrom').val() && featuredateto <= $('#datefrom').val())\n"
                    stylevis += "||\n"
                    stylevis += "(featuredatefrom >= $('#dateto').val() && featuredateto >= $('#dateto').val())\n"
                    stylevis += ") {\n"
                    stylevis += styledef.replace("1.0", "0.0") + "\n"
                    stylevis += "}\n"
                    style = style[:end+1] + stylevis + style[end+2:]
                    f = open(styletimefile, 'w')
                    f.write(style)
                    f.close()
                layerid -= 1
        return layernames
    
    def changeAlpha(self, styledef):
        #TODO rekurze na zmenu u vsech rgb
        rgbastart = styledef.find("rgba")
        rgbaalphastart = styledef.find(",", rgbastart)
        rgbaalphastart = styledef.find(",", rgbaalphastart)
        rgbaalphastart = styledef.find(",", rgbaalphastart)
        rgbaend = styledef.find(")", rgbaalphastart)
