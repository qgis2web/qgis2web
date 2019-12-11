# -*- coding: utf-8 -*-

"""
/***************************************************************************
 Process2Web
                                 A QGIS plugin
 Processing plugin for qgis2web
                              -------------------
        begin                : 2017-04-03
        copyright            : (C) 2017 by Tom Chadwin
        email                : tom.chadwin@nnpa.org.uk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from collections import OrderedDict
import traceback
from qgis.core import (Qgis,
                       QgsProcessing,
                       QgsProject,
                       QgsMapLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterString,
                       QgsProcessingParameterBoolean,
                       QgsMessageLog,
                       QgsWkbTypes)
from qgis.utils import iface

from qgis.core import QgsProcessingAlgorithm
# from processing.tools import dataobjects
from .writerRegistry import (WRITER_REGISTRY)
from .exporter import (EXPORTER_REGISTRY)
from .olwriter import (OpenLayersWriter)
from .leafletWriter import (LeafletWriter)
from .configparams import getDefaultParams

defaultParams = getDefaultParams()


class qgis2webAlgorithm(QgsProcessingAlgorithm):

    def __init__(self):
        super().__init__()

    def createInstance(self):
        return type(self)()

    def group(self):
        return "Export webmap"

    def groupId(self):
        return "exportWebmap"


class exportProject(qgis2webAlgorithm):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    def name(self):
        """This is the provired full name.
        """
        return 'exportProject'

    def displayName(self):
        """This is the provired full name.
        """
        return 'Export project'

    def initAlgorithm(self, config=None):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The branch of the toolbox under which the algorithm will appear
        # self.group = 'Export to webmap'

    def processAlgorithm(self, parameters, context, progress):
        """Here is where the processing itself takes place."""

        writer = WRITER_REGISTRY.createWriterFromProject()
        (writer.layers, writer.groups, writer.popup,
         writer.visible, writer.json,
         writer.cluster) = self.getLayersAndGroups()
        exporter = EXPORTER_REGISTRY.createFromProject()
        write_folder = exporter.exportDirectory()
        writer.write(iface, write_folder)
        return {}

    def getLayersAndGroups(self):
        root_node = QgsProject.instance().layerTreeRoot()
        tree_layers = root_node.findLayers()
        layers = []
        popup = []

        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if (layer.type() != QgsMapLayer.PluginLayer and
                    (layer.type() != QgsMapLayer.VectorLayer or
                     layer.wkbType() != QgsWkbTypes.NoGeometry) and
                    root_node.findLayer(layer.id()).isVisible()):
                try:
                    # if layer.type() == QgsMapLayer.VectorLayer:
                    #    testDump = layer.renderer().dump()
                    layers.append(layer)
                    layerPopups = []
                    if layer.type() == QgsMapLayer.VectorLayer:
                        for field in layer.fields():
                            fieldList = []
                            k = field.name()
                            cProp = "qgis2web/popup/" + field.name()
                            v = layer.customProperty(cProp, "")
                            fieldList.append(k.strip())
                            fieldList.append(v.strip())
                            layerPopups.append(tuple(fieldList))
                    popup.append(OrderedDict(layerPopups))
                except Exception:
                    QgsMessageLog.logMessage(traceback.format_exc(),
                                             "qgis2web",
                                             level=Qgis.Critical)

        visible = []
        json = []
        cluster = []
        for layer in layers:
            visible.append(layer.customProperty("qgis2web/Visible", True))
            json.append(layer.customProperty("qgis2web/Encode to JSON", True))
            cluster.append(layer.customProperty("qgis2web/Cluster", 0) == 2)

        return (layers[::-1],
                {},
                popup[::-1],
                visible[::-1],
                json[::-1],
                cluster[::-1])


class exportLayer(qgis2webAlgorithm):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    OUTPUT_LAYER = 'OUTPUT_LAYER'
    INPUT_LAYER = 'INPUT_LAYER'

    def name(self):
        return "exportLayer"

    def getInputs(self, parameters, context):
        inputExporter = self.parameterAsString(parameters,
                                               "Exporter",
                                               context)
        inputLib = self.parameterAsString(parameters,
                                          "Mapping library location",
                                          context)
        inputJSON = self.parameterAsBool(parameters,
                                         "Minify GeoJSON files",
                                         context)
        inputPrecision = self.parameterAsString(parameters,
                                                "Precision",
                                                context)
        inputExtent = self.parameterAsString(parameters,
                                             "Extent",
                                             context)
        inputMaxZoom = self.parameterAsInt(parameters,
                                           "Max zoom level",
                                           context)
        inputMinZoom = self.parameterAsInt(parameters,
                                           "Min zoom level",
                                           context)
        inputRestrict = self.parameterAsBool(parameters,
                                             "Restrict to extent",
                                             context)
        inputAddress = self.parameterAsBool(parameters,
                                            "Add address search",
                                            context)
        inputLayersList = self.parameterAsBool(parameters,
                                               "Add layers list",
                                               context)
        inputGeolocate = self.parameterAsBool(parameters,
                                              "Geolocate user",
                                              context)
        inputHighlight = self.parameterAsBool(parameters,
                                              "Highlight on hover",
                                              context)
        inputLayerSearch = self.parameterAsString(parameters,
                                                  "Layer search",
                                                  context)
        inputCRS = self.parameterAsBool(parameters,
                                        "Match project CRS",
                                        context)
        inputMeasure = self.parameterAsString(parameters,
                                              "Measure tool",
                                              context)
        inputHover = self.parameterAsBool(parameters,
                                          "Show popups on hover",
                                          context)
        inputTemplate = self.parameterAsString(parameters,
                                               "Template",
                                               context)
        return (inputExporter,
                inputLib,
                inputJSON,
                inputPrecision,
                inputExtent,
                inputMaxZoom,
                inputMinZoom,
                inputRestrict,
                inputAddress,
                inputLayersList,
                inputGeolocate,
                inputHighlight,
                inputLayerSearch,
                inputCRS,
                inputMeasure,
                inputHover,
                inputTemplate)

    def getWriter(self, inputMapFormat):
        if inputMapFormat.lower() == "leaflet":
            writer = LeafletWriter()
        else:
            writer = OpenLayersWriter()
        return writer

    def writerParams(self, writer, inputParams):
        writer.params["Data export"]["Exporter"] = inputParams[0]
        writer.params["Data export"]["Mapping library location"] = (
            inputParams[1])
        writer.params["Data export"]["Minify GeoJSON files"] = inputParams[2]
        writer.params["Data export"]["Precision"] = inputParams[3]
        writer.params["Scale/Zoom"]["Extent"] = inputParams[4]
        writer.params["Scale/Zoom"]["Max zoom level"] = inputParams[5]
        writer.params["Scale/Zoom"]["Min zoom level"] = inputParams[6]
        writer.params["Scale/Zoom"]["Restrict to extent"] = inputParams[7]
        writer.params["Appearance"]["Add address search"] = inputParams[8]
        writer.params["Appearance"]["Add layers list"] = inputParams[9]
        writer.params["Appearance"]["Geolocate user"] = inputParams[10]
        writer.params["Appearance"]["Highlight on hover"] = inputParams[11]
        writer.params["Appearance"]["Layer search"] = inputParams[12]
        writer.params["Appearance"]["Match project CRS"] = inputParams[13]
        writer.params["Appearance"]["Measure tool"] = inputParams[14]
        writer.params["Appearance"]["Show popups on hover"] = inputParams[15]
        writer.params["Appearance"]["Template"] = inputParams[16]


class exportVector(exportLayer):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    def name(self):
        """This is the provired full name.
        """
        return 'exportVectorLayer'

    def displayName(self):
        """This is the provired full name.
        """
        return 'Export vector layer'

    def initAlgorithm(self, config=None):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(QgsProcessingParameterVectorLayer(
            self.INPUT_LAYER,
            'Input vector layer',
            [QgsProcessing.TypeVectorAnyGeometry],
            optional=False))

        self.addParameter(QgsProcessingParameterBoolean("VISIBLE",
                                                        "Visible"))
        self.addParameter(QgsProcessingParameterBoolean("CLUSTER",
                                                        "Cluster"))
        self.addParameter(QgsProcessingParameterString("POPUP",
                                                       "Popup field headers"))
        self.addParameter(QgsProcessingParameterString("EXPORTER",
                                                       "Exporter"))
        self.addParameter(QgsProcessingParameterString(
            "LIBLOC", "Mapping library location"))
        self.addParameter(QgsProcessingParameterBoolean(
            "MINIFY", "Minify GeoJSON files"))
        self.addParameter(QgsProcessingParameterString(
            "PRECISION", "Precision", defaultValue="maintain"))
        self.addParameter(QgsProcessingParameterString("EXTENT",
                                                       "Extent"))
        self.addParameter(QgsProcessingParameterNumber("MAXZOOM",
                                                       "Max zoom level",
                                                       minValue=1,
                                                       maxValue=28,
                                                       defaultValue=28
                                                       ))
        self.addParameter(QgsProcessingParameterNumber("MINZOOM",
                                                       "Min zoom level",
                                                       minValue=1,
                                                       maxValue=28,
                                                       defaultValue=1
                                                       ))
        self.addParameter(QgsProcessingParameterBoolean("RESTRICT",
                                                        "Restrict to extent"))
        self.addParameter(QgsProcessingParameterBoolean("ADDRESS",
                                                        "Add address search"))
        self.addParameter(QgsProcessingParameterBoolean("LAYERSLIST",
                                                        "Add layers list"))
        self.addParameter(QgsProcessingParameterBoolean("GEOLOCATE",
                                                        "Geolocate user"))
        self.addParameter(QgsProcessingParameterBoolean("HIGHLIGHT",
                                                        "Highlight on hover"))
        self.addParameter(QgsProcessingParameterString("SEARCH",
                                                       "Layer search"))
        self.addParameter(QgsProcessingParameterBoolean("CRS",
                                                        "Match project CRS"))
        self.addParameter(QgsProcessingParameterString("MEASURE",
                                                       "Measure tool"))
        self.addParameter(QgsProcessingParameterBoolean(
            "POPUPSHOVER", "Show popups on hover"))
        self.addParameter(QgsProcessingParameterString("TEMPLATE",
                                                       "Template"))

    def processAlgorithm(self, parameters, context, feedback):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputLayer = self.parameterAsVectorLayer(parameters,
                                                 self.INPUT_LAYER,
                                                 context)
        # inputLayer = dataobjects.getObjectFromUri(inputFilename)
        inputVisible = self.parameterAsBool(parameters, "VISIBLE", context)
        inputCluster = self.parameterAsBool(parameters, "CLUSTER", context)
        inputPopup = self.parameterAsString(parameters, "POPUP", context)

        popupList = []
        fields = inputPopup.split(",")
        for field in fields:
            fieldList = []
            k, v = field.split(":")
            fieldList.append(k.strip())
            fieldList.append(v.strip())
            popupList.append(tuple(fieldList))

        inputParams = self.getInputs(parameters, context)

        inputMapFormat = self.parameterAsString(parameters,
                                                "MAP_FORMAT",
                                                context)
        writer = self.getWriter(inputMapFormat)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS object (a
        # QgsVectorLayer in this case) using the
        # processing.getObjectFromUri() method.

        writer.params = defaultParams
        self.writerParams(writer, inputParams)
        writer.layers = [inputLayer]
        writer.groups = {}
        writer.popup = [OrderedDict(popupList)]
        writer.visible = [inputVisible]
        writer.json = [True]
        writer.cluster = [inputCluster]
        writer.json = [True]
        writer.getFeatureInfo = [False]
        exporter = EXPORTER_REGISTRY.createFromProject()
        write_folder = exporter.exportDirectory()
        writer.write(iface, write_folder)

        return {}

    def shortHelp(self):
        return self._formatHelp("""
            <p>Export the selected vector layer as a webmap</p>
            <h2>Inputs</h2>
            <dl>
                <dt>Popup field headers</dt>
                <dd>fieldname: value, fieldname: value, fieldname: value
                    value = no label | inline label | header label</dd>
                <dt>Map format</dt>
                <dd>OpenLayers | Leaflet</dd>
                <dt>Mapping library location</dt>
                <dd>Local | CDN</dd>
                <dt>Exporter</dt>
                <dd>Export to folder | Export to FTP site</dd>
                <dt>Exporter</dt>
                <dd>Export to folder | Export to FTP site</dd>
                <dt>Precision</dt>
                <dd>maintain | [decimal places]</dd>
                <dt>Min zoom level</dt>
                <dd>1-28</dd>
                <dt>Max zoom level</dt>
                <dd>1-28</dd>
                <dt>Extent</dt>
                <dd>Canvas extent | Fit to layers extent</dd>
                <dt>Add layers list</dt>
                <dd>None | collapsed | expanded</dd>
                <dt>Measure tool</dt>
                <dd>None | metric | imperial</dd>
                <dt>Template</dt>
                <dd>[filename]</dd>
                <dt>Layer search</dt>
                <dd>None | layer:field</dd>
            </dl>""")


class exportRaster(exportLayer):
    """This is an example algorithm that takes a vector layer and
    creates a new one just with just those features of the input
    layer that are selected.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the GeoAlgorithm class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    def name(self):
        """This is the provired full name.
        """
        return 'exportRasterLayer'

    def displayName(self):
        """This is the provired full name.
        """
        return 'Export raster layer'

    def initAlgorithm(self, config=None):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(QgsProcessingParameterRasterLayer(
            self.INPUT_LAYER,
            'Input raster layer',
            optional=False))

        self.addParameter(QgsProcessingParameterBoolean(
            "GETFEATUREINFO",
            "Enable GetFeatureInfo"))

    def processAlgorithm(self, parameters, context, feedback):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputLayer = self.parameterAsRasterLayer(parameters,
                                                 self.INPUT_LAYER,
                                                 context)
        inputVisible = self.parameterAsBool(parameters, "VISIBLE", context)
        inputGetFeatureInfo = self.parameterAsBool(parameters,
                                                   "GETFEATUREINFO",
                                                   context)

        inputParams = self.getInputs(parameters, context)

        inputMapFormat = self.parameterAsString(parameters,
                                                "MAP_FORMAT",
                                                context)
        writer = self.getWriter(inputMapFormat)

        writer.params = defaultParams
        self.writerParams(writer, inputParams)
        writer.layers = [inputLayer]
        writer.groups = {}
        writer.popup = [False]
        writer.visible = [inputVisible]
        writer.json = [False]
        writer.getFeatureInfo = [inputGetFeatureInfo]
        writer.cluster = [False]
        exporter = EXPORTER_REGISTRY.createFromProject()
        write_folder = exporter.exportDirectory()
        writer.write(iface, write_folder)

        return {}

    def shortHelp(self):
        return self._formatHelp("""
            <p>Export the selected raster layer as a webmap</p>
            <h2>Inputs</h2>
            <dl>
                <dt>Map format</dt>
                <dd>OpenLayers | Leaflet</dd>
                <dt>Mapping library location</dt>
                <dd>Local | CDN</dd>
                <dt>Exporter</dt>
                <dd>Export to folder | Export to FTP site</dd>
                <dt>Exporter</dt>
                <dd>Export to folder | Export to FTP site</dd>
                <dt>Precision</dt>
                <dd>maintain | [decimal places]</dd>
                <dt>Min zoom level</dt>
                <dd>1-28</dd>
                <dt>Max zoom level</dt>
                <dd>1-28</dd>
                <dt>Extent</dt>
                <dd>Canvas extent | Fit to layers extent</dd>
                <dt>Add layers list</dt>
                <dd>None | collapsed | expanded</dd>
                <dt>Measure tool</dt>
                <dd>None | metric | imperial</dd>
                <dt>Template</dt>
                <dd>[filename]</dd>
            </dl>""")
