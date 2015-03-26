# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgis2web_class
                                 A QGIS plugin
 Export your QGIS map to a webmap
                             -------------------
        begin                : 2015-03-26
        copyright            : (C) 2015 by Riccardo Klinger / Geolicious
        email                : riccardo.klinger@geolicious.de
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load qgis2web_class class from file qgis2web_class.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .qgis2web_mod import qgis2web_class
    return qgis2web_class(iface)
