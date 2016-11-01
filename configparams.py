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
from utils import tempFolder


def getTemplates():
    fl = os.path.join(QgsApplication.qgisSettingsDirPath(),
                      "qgis2web",
                      "templates")
    if not os.path.exists(fl):
        shutil.copytree(os.path.join(os.path.dirname(__file__),
                                     "templates"),
                        fl)
    return tuple(f[:f.find(".")] for f in reversed(os.listdir(fl))
                 if f.endswith("html"))

paramsOL = {
    "Appearance": {
        "Add layers list": False,
        "Match project CRS": False,
        "Add address search": False,
        "Layer search": ("None", "placeholder"),
        "Measure tool": ("None", "Metric", "Imperial"),
        "Show popups on hover": False,
        "Highlight on hover": False,
        "Geolocate user": False,
        "Template": getTemplates()
    },
    "Data export": {
        "Export folder": tempFolder(),
        "Precision": ("maintain", "1", "2", "3", "4", "5", "6", "7", "8",
                      "9", "10", "11", "12", "13", "14", "15"),
        "Minify GeoJSON files": True,
        "Mapping library location": ("Local", "CDN")
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

baselayers = (
            "OSM",
            "OSM B&W",
            "Stamen Toner",
            "OSM DE",
            "OSM HOT",
            "Thunderforest Cycle",
            "Thunderforest Transport",
            "Thunderforest Landscape",
            "Thunderforest Outdoors",
            "OpenMapSurfer Roads",
            "OpenMapSurfer adminb",
            "OpenMapSurfer roadsg",
            "Stamen Terrain",
            "Stamen Terrain background",
            "Stamen Watercolor",
            "OpenWeatherMap Clouds",
            "OpenWeatherMap Precipitation",
            "OpenWeatherMap Rain",
            "OpenWeatherMap Pressure",
            "OpenWeatherMap Wind",
            "OpenWeatherMap Temp",
            "OpenWeatherMap Snow"),


specificParams = {
}

specificOptions = {
}
