# coding=utf-8
"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**QGIS plugin implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

.. note:: This source code was copied from the 'postgis viewer' application
     with original authors:
     Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk
     Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org

"""

__author__ = 'tim@kartoza.com'
__revision__ = '$Format:%H$'
__date__ = '10/01/2011'
__copyright__ = (
    'Copyright (c) 2010 by Ivan Mincik, ivan.mincik@gista.sk and '
    'Copyright (c) 2011 German Carrillo, geotux_tuxman@linuxmail.org'
    'Copyright (c) 2014 Tim Sutton, tim@kartoza.com'
)

import logging

from qgis.core import QgsMapLayerRegistry, QGis, QgsMapLayer
from qgis.gui import QgsMapCanvasLayer  # pylint: disable=no-name-in-module
from PyQt4.QtCore import QObject, pyqtSlot, pyqtSignal


# noinspection PyMethodMayBeStatic,PyPep8Naming
class QgisInterface(QObject):
    """Class to expose qgis objects and functions to plugins.

    This class is here for enabling us to run unit tests only,
    so most methods are simply stubs.
    """
    currentLayerChanged = pyqtSignal(QgsMapCanvasLayer)
    layerSavedAs = pyqtSignal(QgsMapLayer, str)

    def __init__(self, canvas):
        """Constructor
        :param canvas:
        """
        QObject.__init__(self)
        self.canvas = canvas
        # Set up slots so we can mimic the behaviour of QGIS when layers
        # are added.
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().layersAdded.connect(self.addLayers)
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().layerWasAdded.connect(self.addLayer)
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAll.connect(self.removeAllLayers)

        # For processing module
        self.destCrs = None
        # For keeping track of which layer is active in the legend.
        self.active_layer = None

        # In the next section of code, we are going to do some monkey patching
        # to make the QGIS processing framework think that this mock QGIS IFACE
        # instance is the actual one. It will also ensure that the processing
        # algorithms are nicely loaded and available for use.

        # Since QGIS > 2.0, the module is moved from QGisLayers to dataobjects
        # pylint: disable=F0401, E0611
        if QGis.QGIS_VERSION_INT > 20001:
            from processing.tools import dataobjects
        else:
            from processing.core import QGisLayers as dataobjects

        import processing
        from processing.core.Processing import Processing
        # pylint: enable=F0401, E0611
        processing.classFactory(self)

        # We create our own getAlgorithm function below which will will monkey
        # patch in to the Processing class in QGIS in order to ensure that the
        # Processing.initialize() call is made before asking for an alg.

        @staticmethod
        def mock_getAlgorithm(name):
            """
            Modified version of the original getAlgorithm function.

            :param name: Name of the algorithm to load.
            :type name: str

            :return: An algorithm concrete class.
            :rtype: QgsAlgorithm  ?
            """
            Processing.initialize()
            algorithms = list()
            try:
                algorithms = Processing.algs.values()
            except AttributeError:
                algorithms = Processing.algs().values()
            for provider in algorithms:
                if name in provider:
                    return provider[name]
            return None

        # Now we let the monkey loose!
        Processing.getAlgorithm = mock_getAlgorithm
        # We also need to make dataobjects think that this iface is 'the one'
        # Note. the placement here (after the getAlgorithm monkey patch above)
        # is significant, so don't move it!
        dataobjects.iface = self

    def __getattr__(self, *args, **kwargs):
        # It's for processing module
        def dummy(*a, **kwa):
            _ = a, kwa
            return QgisInterface(self.canvas)
        return dummy

    def __iter__(self):
        # It's for processing module
        return self

    def next(self):
        # It's for processing module
        raise StopIteration

    def layers(self):
        # It's for processing module
        # simulate iface.legendInterface().layers()
        return QgsMapLayerRegistry.instance().mapLayers().values()

    @pyqtSlot('QStringList')
    def addLayers(self, layers):
        """Handle layers being added to the registry so they show up in canvas.

        :param layers: list<QgsMapLayer> list of map layers that were added

        .. note:: The QgsInterface api does not include this method,
            it is added here as a helper to facilitate testing.
        """
        # LOGGER.debug('addLayers called on qgis_interface')
        # LOGGER.debug('Number of layers being added: %s' % len(layers))
        # LOGGER.debug('Layer Count Before: %s' % len(self.canvas.layers()))
        current_layers = self.canvas.layers()
        final_layers = []
        # We need to keep the record of the registered layers on our canvas!
        registered_layers = []
        for layer in current_layers:
            final_layers.append(QgsMapCanvasLayer(layer))
            registered_layers.append(layer.id())
        for layer in layers:
            if layer.id() not in registered_layers:
                final_layers.append(QgsMapCanvasLayer(layer))

        self.canvas.setLayerSet(final_layers)
        # LOGGER.debug('Layer Count After: %s' % len(self.canvas.layers()))

    @pyqtSlot('QgsMapLayer')
    def addLayer(self, layer):
        """Handle a layer being added to the registry so it shows up in canvas.

        :param layer: list<QgsMapLayer> list of map layers that were added

        .. note: The QgsInterface api does not include this method, it is added
                 here as a helper to facilitate testing.

        .. note: The addLayer method was deprecated in QGIS 1.8 so you should
                 not need this method much.
        """
        pass

    @pyqtSlot()
    def removeAllLayers(self, ):
        """Remove layers from the canvas before they get deleted.

        .. note:: This is NOT part of the QGisInterface API but is needed
            to support QgsMapLayerRegistry.removeAllLayers().

        """
        self.canvas.setLayerSet([])
        self.active_layer = None

    def newProject(self):
        """Create new project."""
        # noinspection PyArgumentList
        QgsMapLayerRegistry.instance().removeAllMapLayers()

    # ---------------- API Mock for QgsInterface follows -------------------

    def zoomFull(self):
        """Zoom to the map full extent."""
        pass

    def zoomToPrevious(self):
        """Zoom to previous view extent."""
        pass

    def zoomToNext(self):
        """Zoom to next view extent."""
        pass

    def zoomToActiveLayer(self):
        """Zoom to extent of active layer."""
        pass

    def addVectorLayer(self, path, base_name, provider_key):
        """Add a vector layer.

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str

        :param provider_key: Provider key e.g. 'ogr'
        :type provider_key: str
        """
        pass

    def addRasterLayer(self, path, base_name):
        """Add a raster layer given a raster layer file name

        :param path: Path to layer.
        :type path: str

        :param base_name: Base name for layer.
        :type base_name: str
        """
        pass

    def setActiveLayer(self, layer):
        """Set the currently active layer in the legend.
        :param layer: Layer to make active.
        :type layer: QgsMapLayer, QgsVectorLayer, QgsRasterLayer
        """
        self.active_layer = layer

    def activeLayer(self):
        """Get pointer to the active layer (layer selected in the legend)."""
        if self.active_layer is not None:
            return self.active_layer
        else:
            return None

    def addToolBarIcon(self, action):
        """Add an icon to the plugins toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass

    def removeToolBarIcon(self, action):
        """Remove an action (icon) from the plugin toolbar.

        :param action: Action to add to the toolbar.
        :type action: QAction
        """
        pass

    def addToolBar(self, name):
        """Add toolbar with specified name.

        :param name: Name for the toolbar.
        :type name: str
        """
        pass

    def mapCanvas(self):
        """Return a pointer to the map canvas."""
        return self.canvas

    def mainWindow(self):
        """Return a pointer to the main window.

        In case of QGIS it returns an instance of QgisApp.
        """
        pass

    def addDockWidget(self, area, dock_widget):
        """Add a dock widget to the main window.

        :param area: Where in the ui the dock should be placed.
        :type area:

        :param dock_widget: A dock widget to add to the UI.
        :type dock_widget: QDockWidget
        """
        pass

    def legendInterface(self):
        """Get the legend.

        TODO: Implement this when it is needed one day...

        See also discussion at:

        https://github.com/AIFDR/inasafe/pull/924/
        """
        return self.canvas
