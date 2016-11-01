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
        'OSM': 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        'OSM B&W': ('http://{s}.www.toolserver.org/tiles/bw-mapnik/' +
                    '{z}/{x}/{y}.png'),
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
        'Stamen Terrain': 'http://a.tile.stamen.com/terrain/{z}/{x}/{y}.png',
        'Stamen Terrain background': ('http://stamen-tiles-a.a.ssl.' +
                                      'fastly.net/terrain-background/{z}/{x}' +
                                      '/{y}.png'),
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
    basemaps = {
        "Stamen Watercolor": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.Stamen({{
        layer: 'watercolor'
    }})
}})""",
        "Stamen Toner": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
        source: new ol.source.Stamen({{
        layer: 'toner'
        }})
}})""",
        "Stamen Terrain": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.Stamen({{
        layer: 'terrain'
    }})
}})""",
        "Stamen Terrain background": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: \
'http://stamen-tiles-{{a-c}}.a.ssl.fastly.net/terrain-background/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OSM": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.OSM()
}})""",
        "OSM B&W": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: \
'http://{{a-c}}.www.toolserver.org/tiles/bw-mapnik/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "Thunderforest Transport": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.thunderforest.com/transport/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "Thunderforest Landscape": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.thunderforest.com/landscape/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "Thunderforest Outdoors": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.thunderforest.com/outdoors/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenMapSurfer Roads": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: \
'http://openmapsurfer.uni-hd.de/tiles/roads/x={{x}}&y={{y}}&z={{z}}',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenMapSurfer adminb": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: \
'http://openmapsurfer.uni-hd.de/tiles/adminb/x={{x}}&y={{y}}&z={{z}}',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenMapSurfer roadsg": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: \
'http://openmapsurfer.uni-hd.de/tiles/roadsg/x={{x}}&y={{y}}&z={{z}}',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OSM HOT": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://{{a-c}}.tile.openstreetmap.fr/hot/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenSeaMap": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://t1.openseamap.org/seamark/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "Thunderforest Cycle": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.thunderforest.com/cycle/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OSM DE": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.openstreetmap.de/tiles/osmde/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenWeatherMap Clouds": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.openweathermap.org/map/clouds/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenWeatherMap Precipitation": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url:'http://tile.openweathermap.org/map/precipitation/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenWeatherMap Rain": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.openweathermap.org/map/rain/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenWeatherMap Pressure": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: \
'http://tile.openweathermap.org/map/pressure/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenWeatherMap Wind": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.openweathermap.org/map/wind/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenWeatherMap Temp": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.openweathermap.org/map/temp/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})""",
        "OpenWeatherMap Snow": """
new ol.layer.Tile({{
    'title': '{title}',
    'type': 'base',
    source: new ol.source.XYZ({{
        url: 'http://tile.openweathermap.org/map/snow/{{z}}/{{x}}/{{y}}.png',
        attributions: [new ol.Attribution({{html: '{attr}'}})]
    }})
}})"""
    }
    basemaps = {k: v.format(**{'title': k, 'attr': basemapAttributions[k]})
                for k, v in basemaps.iteritems()}
    return basemaps

basemapAttributions = {
    'OSM': """\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors,\
<a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>""",
    'OSM B&W': """\
&copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, \
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
    'Stamen Terrain': """\
Map tiles by <a href="http://stamen.com">Stamen Design</a>,\
<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash;\
Map data: &copy; <a href="http://openstreetmap.org">OpenStreetMap</a>\
contributors,<a href="http://creativecommons.org/licenses/by-sa/2.0/">\
CC-BY-SA</a>""",
    'Stamen Terrain background': """\
Map tiles by <a href="http://stamen.com">Stamen Design</a>, \
<a href="http://creativecommons.org/licenses/by/3.0">CC BY 3.0</a> &mdash; \
Map data &copy; <a href="http://www.openstreetmap.org/copyright">\
OpenStreetMap</a>""",
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
