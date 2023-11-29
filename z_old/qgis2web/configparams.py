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

from qgis.core import QgsApplication
import os
import shutil
from qgis2web.exporter import EXPORTER_REGISTRY
from qgis.gui import QgsColorButton
from qgis.PyQt.QtGui import QColor


def getTemplates():
    src = os.path.join(os.path.dirname(__file__), "templates")
    dst = os.path.join(QgsApplication.qgisSettingsDirPath(), "qgis2web",
                       "templates")
    if not os.path.exists(dst):
        shutil.copytree(src, dst)
    else:
        for fname in os.listdir(src):
            with open(os.path.join(src, fname)) as s:
                srcCode = s.read()
            with open(os.path.join(dst, os.path.basename(fname)), 'w') as d:
                d.seek(0)
                d.write(srcCode)
                d.truncate()
    return tuple(f[:f.find(".")] for f in reversed(os.listdir(dst))
                 if f.endswith("html"))


def getParams(configure_exporter_action=None):

    accentColor = QgsColorButton()
    accentColor.setColor(QColor(0, 0, 0))
    backgroundColor = QgsColorButton()
    backgroundColor.setColor(QColor(248, 248, 248))

    params = {
        "Appearance": {
            "Add layers list": ("None", "Collapsed", "Expanded"),
            "Match project CRS": False,
            "Add address search": False,
            "Add abstract": ("None", "upper right", "lower right",
                             "lower left", "upper left"),
            "Layer search": ("None", "placeholder"),
            "Attribute filter": ["None", "placeholder2"],
            "Measure tool": ("None", "Metric", "Imperial"),
            "Show popups on hover": False,
            "Highlight on hover": False,
            "Geolocate user": False,
            "Template": getTemplates(),
            "Widget Icon": accentColor,
            "Widget Background": backgroundColor
        },
        "Data export": {
            "Precision": ("maintain", "1", "2", "3", "4", "5", "6", "7", "8",
                          "9", "10", "11", "12", "13", "14", "15"),
            "Minify GeoJSON files": True
        },
        "Scale/Zoom": {
            "Extent": ("Canvas extent", "Fit to layers extent"),
            "Restrict to extent": False,
            "Max zoom level": ("1", "2", "3", "4", "5", "6", "7",
                               "8", "9", "10", "11", "12", "13", "14",
                               "15", "16", "17", "18", "19", "20", "21",
                               "22", "23", "24", "25", "26", "27", "28"),
            "Min zoom level": ("1", "2", "3", "4", "5", "6", "7",
                               "8", "9", "10", "11", "12", "13", "14",
                               "15", "16", "17", "18", "19", "20", "21",
                               "22", "23", "24", "25", "26", "27", "28"),
        }
    }

    if configure_exporter_action:
        params["Data export"]["Exporter"] = {'option':
                                             EXPORTER_REGISTRY.getOptions(),
                                             'action':
                                             configure_exporter_action}
    else:
        params["Data export"]["Exporter"] = EXPORTER_REGISTRY.getOptions()

    return params


def getDefaultParams():
    params = getParams()
    for group, settings in params.items():
        for param, value in settings.items():
            if isinstance(value, tuple):
                if param == 'Max zoom level':
                    settings[param] = value[-1]
                elif param == 'Template':
                    settings[param] = value[1]
                else:
                    settings[param] = value[0]
            if isinstance(value, list):
                if param == 'Attribute filter':
                    settings[param] = value[0]
                else:
                    settings[param] = value[0]
            if param in ('Widget Icon', 'Widget Background'):
                settings[param] = value.color().name()
    params['Appearance']['Search layer'] = None
    params['Appearance']['Attribute filter'] = []
    return params


specificParams = {
    "Add abstract": "leaflet",
    "Attribute filter": "leaflet"
}

specificOptions = {
}
