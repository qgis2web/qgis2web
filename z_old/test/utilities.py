# coding=utf-8
"""Common functionality used by regression tests."""

import os
import sys
import logging

from qgis.core import QgsVectorLayer, QgsRasterLayer, QgsProject


LOGGER = logging.getLogger('QGIS')
QGIS_APP = None  # Static variable used to hold hand to running QGIS app
CANVAS = None
IFACE = None
PARENT = None


def get_qgis_app():
    """ Start one QGIS application to test against.

    :returns: Handle to QGIS app, canvas, iface and parent. If there are any
        errors the tuple members will be returned as None.
    :rtype: (QgsApplication, CANVAS, IFACE, PARENT)

    If QGIS is already running the handle to that app will be returned.
    """

    try:
        from PyQt4 import QtGui, QtCore
        from qgis.core import QgsApplication
        from qgis.gui import QgsMapCanvas
        from test.qgis_interface import QgisInterface
    except ImportError:
        return None, None, None, None

    global QGIS_APP  # pylint: disable=W0603

    if QGIS_APP is None:
        gui_flag = True  # All test will run qgis in gui mode
        # noinspection PyPep8Naming
        QGIS_APP = QgsApplication(sys.argv, gui_flag)
        # Make sure QGIS_PREFIX_PATH is set in your env if needed!
        QGIS_APP.initQgis()
        s = QGIS_APP.showSettings()
        LOGGER.debug(s)

    global PARENT  # pylint: disable=W0603
    if PARENT is None:
        PARENT = QtGui.QWidget()

    global CANVAS  # pylint: disable=W0603
    if CANVAS is None:
        CANVAS = QgsMapCanvas(PARENT)
        CANVAS.resize(QtCore.QSize(800, 600))

    global IFACE  # pylint: disable=W0603
    if IFACE is None:
        # QgisInterface is a stub implementation of the QGIS plugin interface
        # noinspection PyPep8Naming
        IFACE = QgisInterface(CANVAS)

    return QGIS_APP, CANVAS, IFACE, PARENT


def get_test_data_path(*args):
    """Return the absolute path to the test data or directory path.

    :param args: List of path.
    :type args: list

    :return: Absolute path to the test data or dir path.
    :rtype: str

    """
    path = os.path.dirname(__file__)
    path = os.path.abspath(os.path.join(path, 'data'))
    for item in args:
        path = os.path.abspath(os.path.join(path, item))

    return path


def load_layer(layer_path):
    """Helper to load and return a single QGIS layer.

    :param layer_path: Path name to raster or vector file.
    :type layer_path: str

    :returns: Layer instance.
    :rtype: QgsMapLayer
    """
    
    QgsProject.instance().clear()
    # Extract basename and absolute path
    file_name = os.path.split(layer_path)[-1]  # In case path was absolute
    base_name, extension = os.path.splitext(file_name)

    # Create QGis Layer Instance
    if extension in ['.asc', '.tif', '.png']:
        layer = QgsRasterLayer(layer_path, base_name)
    elif extension in ['.shp']:
        layer = QgsVectorLayer(layer_path, base_name, 'ogr')
    else:
        message = 'File %s had illegal extension' % layer_path
        raise Exception(message)

    # noinspection PyUnresolvedReferences
    message = 'Layer "%s" is not valid' % layer.source()
    # noinspection PyUnresolvedReferences
    if not layer.isValid():
        print(message)
    # noinspection PyUnresolvedReferences
    if not layer.isValid():
        raise Exception(message)
    return layer


def load_wfs_layer(url, name):
    """Helper to load wfs layer and load it as QGIS layer.

    :param url: The complete URL to the WFS layer.
    :type url: str

    :param name: The layer name.
    :type name: str

    :returns: Layer instance.
    :rtype: QgsMapLayer
    """

    QgsProject.instance().clear()
    layer = QgsVectorLayer(url, name, 'WFS')
    # noinspection PyUnresolvedReferences
    message = 'Layer "%s" is not valid' % layer.source()
    # noinspection PyUnresolvedReferences
    if not layer.isValid():
        print(message)
    # noinspection PyUnresolvedReferences
    if not layer.isValid():
        raise Exception(message)
    return layer


def load_wms_layer(url, name):
    """Helper to load wms layer and load it as QGIS layer.

    :param url: The complete URL to the WMS layer.
    :type url: str

    :param name: The layer name.
    :type name: str

    :returns: Layer instance.
    :rtype: QgsMapLayer
    """

    QgsProject.instance().clear()
    layer = QgsRasterLayer(url, name, 'wms')
    # noinspection PyUnresolvedReferences
    message = 'Layer "%s" is not valid' % layer.source()
    # noinspection PyUnresolvedReferences
    if not layer.isValid():
        print(message)
    # noinspection PyUnresolvedReferences
    if not layer.isValid():
        raise Exception(message)
    return layer
