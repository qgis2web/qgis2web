# -*- coding: utf-8 -*-
"""
/***************************************************************************
 qgis2leaf @ Social Planing Council of the City of Ottawa
                                 A QGIS plugin
 QGIS to Leaflet creation programm
                             -------------------
        begin                : 2014-04-29
        copyright            : (C) 2013 by Riccardo Klinger
        email                : riccardo.klinger@geolicious.com
 ***************************************************************************/
/***************************************************************************
INSTRUCTION ON FILE USAGE:
***************************************************************************/
"""
# To add a line to the layer list you might use this dictionary python
# variable. Its first element is the basemap service name which will be
# displayed in the GUI. The second entry marked with "META" is the metadata for
# the leaflet. Please respect copyrights and licenses
# After you've added a basemap service, the plugin needs to be reinstalled.
#
"""
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""


def basemapLeaflet():
    dictionary = {
        'OSM Standard': 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'Stamen Toner': 'http://a.tile.stamen.com/toner/{z}/{x}/{y}.png',
        'OSM DE': ('http://{s}.tile.openstreetmap.de/tiles/' +
                   'osmde/{z}/{x}/{y}.png'),
        'OSM HOT': 'http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        'Thunderforest Cycle': ('http://{s}.tile.thunderforest.com/cycle/' +
                                '{z}/{x}/{y}.png'),
        'Thunderforest Transport': ('http://{s}.tile.thunderforest.com/' +
                                    'transport/{z}/{x}/{y}.png'),
        'Thunderforest Landscape': ('http://{s}.tile.thunderforest.com/' +
                                    'landscape/{z}/{x}/{y}.png'),
        'Thunderforest Outdoors': ('http://{s}.tile.thunderforest.com/' +
                                   'outdoors/{z}/{x}/{y}.png'),
        'OpenMapSurfer Roads': ('http://openmapsurfer.uni-hd.de/tiles/' +
                                'roads/x={x}&y={y}&z={z}'),
        'OpenMapSurfer adminb': ('http://openmapsurfer.uni-hd.de/tiles/' +
                                 'adminb/x={x}&y={y}&z={z}'),
        'OpenMapSurfer roadsg': ('http://openmapsurfer.uni-hd.de/tiles/' +
                                 'roadsg/x={x}&y={y}&z={z}'),
        'MapQuestOpen OSM': ('http://otile1.mqcdn.com/tiles/1.0.0/map/' +
                             '{z}/{x}/{y}.jpeg'),
        'MapQuestOpen Aerial': ('http://otile1.mqcdn.com/tiles/1.0.0/sat/' +
                                '{z}/{x}/{y}.jpg'),
        'Stamen Terrain': 'http://a.tile.stamen.com/terrain/{z}/{x}/{y}.png',
        'Stamen Watercolor': ('http://a.tile.stamen.com/watercolor/' +
                              '{z}/{x}/{y}.png'),
        'OpenWeatherMap Clouds': ('http://{s}.tile.openweathermap.org/map/' +
                                  'clouds/{z}/{x}/{y}.png'),
        'OpenWeatherMap Precipitation': ('http://{s}.tile.openweathermap.org' +
                                         '/map/precipitation/{z}/{x}/{y}.png'),
        'OpenWeatherMap Rain': ('http://{s}.tile.openweathermap.org/map/' +
                                'rain/{z}/{x}/{y}.png'),
        'OpenWeatherMap Pressure': ('http://{s}.tile.openweathermap.org/' +
                                    'map/pressure/{z}/{x}/{y}.png'),
        'OpenWeatherMap Wind': ('http://{s}.tile.openweathermap.org/map/' +
                                'wind/{z}/{x}/{y}.png'),
        'OpenWeatherMap Temp': ('http://{s}.tile.openweathermap.org/map/' +
                                'temp/{z}/{x}/{y}.png'),
        'OpenWeatherMap Snow': ('http://{s}.tile.openweathermap.org/map/' +
                                'snow/{z}/{x}/{y}.png'),
        'OpenSeaMap': 'http://tiles.openseamap.org/seamark/{z}/{x}/{y}.png'
    }
    return dictionary


def basemapOL():
    dictionary = {
        "Stamen Watercolor": """new ol.layer.Tile({
                                    title: 'Stamen watercolor',
                                    source: new ol.source.Stamen({
                                        layer: 'watercolor'
                                    })
                                })""",
        "Stamen Toner": """new ol.layer.Tile({title: 'Stamen toner',
                                              source: new ol.source.Stamen({
                                                layer: 'toner'
                                              })
                                            })""",
        "Stamen Terrain": """new ol.layer.Tile({title: 'Stamen terrain',
                                                source: new ol.source.Stamen({
                                                    layer: 'terrain'
                                                })
                                              })""",
        "OSM Standard": """new ol.layer.Tile({title: 'OSM',
                                              source: new ol.source.OSM()
                                            })""",
        "MapQuestOpen OSM": """new ol.layer.Tile({
                                    title: 'MapQuest OSM',
                                    source: new ol.source.MapQuest({
                                        layer: 'osm'
                                    })
                               })""",
        "MapQuestOpen Aerial": """new ol.layer.Tile({
                                    title: 'MapQuest Aerial',
                                    source: new ol.source.MapQuest({
                                        layer: 'sat'
                                    })
                                  })""",
        "Thunderforest Transport": """
new ol.layer.Tile({
    title: 'Thunderforest Transport',
    source: new ol.source.XYZ({
        url: 'http://tile.thunderforest.com/transport/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['Thunderforest Transport'],
        "Thunderforest Landscape": """
new ol.layer.Tile({
    title: 'Thunderforest Landscape',
    source: new ol.source.XYZ({
        url: 'http://tile.thunderforest.com/landscape/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['Thunderforest Landscape'],
        "Thunderforest Outdoors": """
new ol.layer.Tile({
    title: 'Thunderforest Outdoors',
    source: new ol.source.XYZ({
        url: 'http://tile.thunderforest.com/outdoors/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['Thunderforest Outdoors'],
        "OpenMapSurfer Roads": """
new ol.layer.Tile({
    title: 'OpenMapSurfer Roads',
    source: new ol.source.XYZ({
        url: 'http://openmapsurfer.uni-hd.de/tiles/roads/x={x}&y={y}&z={z}',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenMapSurfer Roads'],
        "OpenMapSurfer adminb": """
new ol.layer.Tile({
    title: 'OpenMapSurfer adminb',
    source: new ol.source.XYZ({
        url: 'http://openmapsurfer.uni-hd.de/tiles/adminb/x={x}&y={y}&z={z}',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenMapSurfer adminb'],
        "OpenMapSurfer roadsg": """
new ol.layer.Tile({
    title: 'OpenMapSurfer roadsg',
    source: new ol.source.XYZ({
        url: 'http://openmapsurfer.uni-hd.de/tiles/roadsg/x={x}&y={y}&z={z}',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenMapSurfer roadsg'],
        "OSM HOT": """
new ol.layer.Tile({
    title: 'OSM HOT',
    source: new ol.source.XYZ({
        url: 'http://{a-c}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OSM HOT'],
        "OpenSeaMap": """
new ol.layer.Tile({
    title: 'OpenSeaMap',
    source: new ol.source.XYZ({
        url: 'http://t1.openseamap.org/seamark/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenSeaMap'],
        "Thunderforest Cycle": """
new ol.layer.Tile({
    title: 'Thunderforest Cycle',
    source: new ol.source.XYZ({
        url: 'http://tile.thunderforest.com/cycle/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['Thunderforest Cycle'],
        "OSM DE": """
new ol.layer.Tile({
    title: 'OSM DE',
    source: new ol.source.XYZ({
        url: 'http://tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OSM DE'],
        "OpenWeatherMap Clouds": """
new ol.layer.Tile({
    title: 'OpenWeatherMap Clouds',
    source: new ol.source.XYZ({
        url: 'http://tile.openweathermap.org/map/clouds/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenWeatherMap Clouds'],
        "OpenWeatherMap Precipitation": """
new ol.layer.Tile({
    title: 'OpenWeatherMap Precipitation',
    source: new ol.source.XYZ({
        url:'http://tile.openweathermap.org/map/precipitation/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenWeatherMap Precipitation'],
        "OpenWeatherMap Rain": """
new ol.layer.Tile({
    title: 'OpenWeatherMap Rain',
    source: new ol.source.XYZ({
        url: 'http://tile.openweathermap.org/map/rain/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenWeatherMap Rain'],
        "OpenWeatherMap Pressure": """
new ol.layer.Tile({
    title: 'OpenWeatherMap Pressure',
    source: new ol.source.XYZ({
        url: 'http://tile.openweathermap.org/map/pressure/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenWeatherMap Pressure'],
        "OpenWeatherMap Wind": """
new ol.layer.Tile({
    title: 'OpenWeatherMap Wind',
    source: new ol.source.XYZ({
        url: 'http://tile.openweathermap.org/map/wind/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenWeatherMap Wind'],
        "OpenWeatherMap Temp": """
new ol.layer.Tile({
    title: 'OpenWeatherMap Temp',
    source: new ol.source.XYZ({
        url: 'http://tile.openweathermap.org/map/temp/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenWeatherMap Temp'],
        "OpenWeatherMap Snow": """
new ol.layer.Tile({
    title: 'OpenWeatherMap Snow',
    source: new ol.source.XYZ({
        url: 'http://tile.openweathermap.org/map/snow/{z}/{x}/{y}.png',
        attributions: [new ol.Attribution({html:'%s'})]
    })
})""" % basemapAttributions()['OpenWeatherMap Snow']
    }
    return dictionary


def basemapAttributions():
    dictionary = {
        'OSM Standard': """\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'Stamen Toner': """\
Map tiles by <a href="http://stamen.com">Stamen Design</a>,\
<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; Map\
data: &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>\
contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'OSM DE': """\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'OSM HOT': """\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>,\
Tiles courtesy of <a href="http://hot.openstreetmap.org/" target="_blank">\
Humanitarian OpenStreetMap Team</a>""",
        'OpenSeaMap': """\
Map data: &copy; <a href="http://www.openseamap.org">OpenSeaMap</a>\
contributors""",
        'Thunderforest Cycle': """\
&copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>,\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'Thunderforest Transport': """\
&copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>,\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'Thunderforest Landscape': """\
&copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>,\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'Thunderforest Outdoors': """\
&copy; <a href="http://www.opencyclemap.org">OpenCycleMap</a>,\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'OpenMapSurfer Roads': """\
Imagery from <a href="http://giscience.uni-hd.de/">GIScience Research Group @\
University of Heidelberg</a> &mdash; Map data:\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'OpenMapSurfer adminb': """\
Imagery from <a href="http://giscience.uni-hd.de/">GIScience Research Group @\
University of Heidelberg</a> &mdash; Map data:\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'OpenMapSurfer roadsg': """\
Imagery from <a href="http://giscience.uni-hd.de/">GIScience Research Group @\
University of Heidelberg</a> &mdash; Map data:\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
        'MapQuestOpen OSM': """\
Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash;\
Map data: &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>\
contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">\
CC-BY-SA</a>""",
        'MapQuestOpen Aerial': """\
Tiles Courtesy of <a href="http://www.mapquest.com/">MapQuest</a> &mdash;\
Portions Courtesy NASA/JPL-Caltech and U.S. Depart. of Agriculture,\
Farm Service Agency""",
        'Stamen Terrain': """\
Map tiles by <a href="http://stamen.com">Stamen Design</a>,\
<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash;\
Map data: &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>\
contributors,<a href="http://creativecommons.org/licenses/by-sa/2.0/">\
CC-BY-SA</a>""",
        'Stamen Watercolor': """\
Map tiles by <a href="http://stamen.com">Stamen Design</a>,\
<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash;\
Map data: &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>\
contributors,<a href="http://creativecommons.org/licenses/by-sa/2.0/">\
CC-BY-SA</a>""",
        'OpenWeatherMap Clouds': """\
Map data &copy; <a href="http://openweathermap.org">OpenWeatherMap</a>""",
        'OpenWeatherMap Precipitation': """\
Map data &copy; <a href="http://openweathermap.org">OpenWeatherMap</a>""",
        'OpenWeatherMap Rain': """\
Map data &copy; <a href="http://openweathermap.org">OpenWeatherMap</a>""",
        'OpenWeatherMap Pressure': """\
Map data &copy; <a href="http://openweathermap.org">OpenWeatherMap</a>""",
        'OpenWeatherMap Wind': """\
Map data &copy; <a href="http://openweathermap.org">OpenWeatherMap</a>""",
        'OpenWeatherMap Temp': """\
Map data &copy; <a href="http://openweathermap.org">OpenWeatherMap</a>""",
        'OpenWeatherMap Snow': """\
Map data &copy; <a href="http://openweathermap.org">OpenWeatherMap</a>"""
    }
    return dictionary
