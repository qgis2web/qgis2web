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
from qgis.core import (QgsProject,
                       QgsMapLayer,
                       QgsVectorLayer,
                       QgsMessageLog)
from qgis.utils import iface

from processing.core.GeoAlgorithm import GeoAlgorithm
from processing.core.parameters import ParameterVector
from processing.tools import dataobjects
from writerRegistry import (WRITER_REGISTRY)
from exporter import (EXPORTER_REGISTRY)

__author__ = 'Tom Chadwin'
__date__ = '2017-04-03'
__copyright__ = '(C) 2017 by Tom Chadwin'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'


class exportProject(GeoAlgorithm):
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

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Export project'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Export to webmap'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        # self.addParameter(ParameterMultipleInput(self.INPUT_LAYER,
        #     self.tr('Input layers'), False))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        # inputFilename = self.getParameterValue(self.INPUT_LAYER)
        writer = WRITER_REGISTRY.createWriterFromProject()
        (writer.layers, writer.groups, writer.popup,
         writer.visible, writer.json,
         writer.cluster) = self.getLayersAndGroups()
        exporter = EXPORTER_REGISTRY.createFromProject()
        write_folder = exporter.exportDirectory()
        writer.write(iface, write_folder)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS object (a
        # QgsVectorLayer in this case) using the
        # processing.getObjectFromUri() method.
        # vectorLayer = dataobjects.getObjectFromUri(inputFilename)

        # And now we can process

        # First we create the output layer. The output value entered by
        # the user is a string containing a filename, so we can use it
        # directly
        # settings = QSettings()
        # systemEncoding = settings.value('/UI/encoding', 'System')
        # provider = vectorLayer.dataProvider()
        # writer = QgsVectorFileWriter(output, systemEncoding,
        #                              provider.fields(),
        #                              provider.geometryType(), provider.crs())

        # Now we take the features from input layer and add them to the
        # output. Method features() returns an iterator, considering the
        # selection that might exist in layer and the configuration that
        # indicates should algorithm use only selected features or all
        # of them
        # features = vector.features(vectorLayer)
        # for f in features:
        #     writer.addFeature(f)

        # There is nothing more to do here. We do not have to open the
        # layer that we have created. The framework will take care of
        # that, or will handle it if this algorithm is executed within
        # a complex model

    def getLayersAndGroups(self):
        root_node = QgsProject.instance().layerTreeRoot()
        tree_layers = root_node.findLayers()
        layers = []

        for tree_layer in tree_layers:
            layer = tree_layer.layer()
            if (layer.type() != QgsMapLayer.PluginLayer and
                    root_node.findLayer(layer.id()).isVisible()):
                try:
                    if layer.type() == QgsMapLayer.VectorLayer:
                        testDump = layer.rendererV2().dump()
                    layers.append(layer)
                except:
                    QgsMessageLog.logMessage(traceback.format_exc(),
                                             "qgis2web",
                                             level=QgsMessageLog.CRITICAL)

        popup = []
        visible = []
        json = []
        cluster = []
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:        
                layerPopups = getPopup(layer)
            else:
                layerPopups = []
            popup.append(OrderedDict(layerPopups))
            visible.append(layer.customProperty("qgis2web/Visible", True))
            json.append(layer.customProperty("qgis2web/Encode to JSON", True))
            cluster.append(layer.customProperty("qgis2web/Cluster", 0) == 2)

        return (layers[::-1],
                {},
                popup[::-1],
                visible[::-1],
                json[::-1],
                cluster[::-1])

                
class exportVector(GeoAlgorithm):
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

    def defineCharacteristics(self):
        """Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # The name that the user will see in the toolbox
        self.name = 'Export vector layer'

        # The branch of the toolbox under which the algorithm will appear
        self.group = 'Export to webmap'

        # We add the input vector layer. It can have any kind of geometry
        # It is a mandatory (not optional) one, hence the False argument
        self.addParameter(ParameterVector(self.INPUT_LAYER,
            self.tr('Input vector layer'),
            ParameterVector.VECTOR_TYPE_ANY,
            False))

    def processAlgorithm(self, progress):
        """Here is where the processing itself takes place."""

        # The first thing to do is retrieve the values of the parameters
        # entered by the user
        inputFilename = self.getParameterValue(self.INPUT_LAYER)

        # Input layers vales are always a string with its location.
        # That string can be converted into a QGIS object (a
        # QgsVectorLayer in this case) using the
        # processing.getObjectFromUri() method.
        vectorLayer = dataobjects.getObjectFromUri(inputFilename)

        writer = WRITER_REGISTRY.createWriterFromProject()
        writer.layers = [vectorLayer]
        writer.groups = {}
        writer.popup = [OrderedDict(getPopup(vectorLayer))]
        writer.visible = [True]
        writer.json = [True]
        writer.cluster = [False]
        exporter = EXPORTER_REGISTRY.createFromProject()
        write_folder = exporter.exportDirectory()
        writer.write(iface, write_folder)

        # And now we can process

        # First we create the output layer. The output value entered by
        # the user is a string containing a filename, so we can use it
        # directly
        # settings = QSettings()
        # systemEncoding = settings.value('/UI/encoding', 'System')
        # provider = vectorLayer.dataProvider()
        # writer = QgsVectorFileWriter(output, systemEncoding,
        #                              provider.fields(),
        #                              provider.geometryType(), provider.crs())

        # Now we take the features from input layer and add them to the
        # output. Method features() returns an iterator, considering the
        # selection that might exist in layer and the configuration that
        # indicates should algorithm use only selected features or all
        # of them
        # features = vector.features(vectorLayer)
        # for f in features:
        #     writer.addFeature(f)

        # There is nothing more to do here. We do not have to open the
        # layer that we have created. The framework will take care of
        # that, or will handle it if this algorithm is executed within
        # a complex model


def getPopup(layer):
    options = []
    layerPopups = []
    fields = layer.pendingFields()
    for f in fields:
        fieldIndex = fields.indexFromName(unicode(f.name()))
        formCnf = layer.editFormConfig()
        editorWidget = formCnf.widgetType(fieldIndex)
        if editorWidget == QgsVectorLayer.Hidden or \
           editorWidget == 'Hidden':
            continue
        options.append(f.name())
    for option in options:
        custProp = layer.customProperty("qgis2web/popup/" + option)
        pair = (option, custProp)
        layerPopups.append(pair)
    return layerPopups
