import re
import os
import shutil
from qgis.PyQt.QtCore import QDir
from qgis.core import QgsDataSourceUri
from qgis2web.utils import safeName


def writeFiles(folder, restrictToExtent, feedback):
    feedback.showFeedback("Exporting libraries...")
    imagesFolder = os.path.join(folder, "images")
    QDir().mkpath(imagesFolder)
    dst = os.path.join(folder, "resources")
    # copy icons
    fontDir = os.path.dirname(__file__) + os.sep + 'webfonts' + os.sep
    fontStore = os.path.join(folder, 'webfonts')
    os.makedirs(fontStore)
    fontStore += os.sep
    shutil.copyfile(fontDir + 'fa-solid-900.woff2',
                    fontStore + 'fa-solid-900.woff2')
    shutil.copyfile(fontDir + 'fa-solid-900.ttf',
                    fontStore + 'fa-solid-900.ttf')
    # copy the rest
    if not os.path.exists(dst):
        shutil.copytree(os.path.join(os.path.dirname(__file__),
                                     "resources"),
                        dst)
    feedback.completeStep()


def writeHTMLstart(settings, controlCount, osmb, feedback):
    feedback.showFeedback("Writing HTML...")
    jsAddress = """<script src="resources/polyfills.js"></script>
        <script src="./resources/functions.js"></script>"""
    cssAddress = """<link rel="stylesheet" href="./resources/ol.css">"""
    jsAddress += """
        <script src="./resources/ol.js"></script>"""
    cssAddress += """
        <link rel="stylesheet" href="resources/fontawesome-all.min.css">"""
    if osmb != "":
        jsAddress += """
        <script src="resources/OSMBuildings-OL3.js"></script>"""
    feedback.completeStep()
    return (jsAddress, cssAddress, controlCount)


def writeLayerSearch(cssAddress, jsAddress, controlCount, layerSearch,
                     searchLayer, feedback):
    feedback.showFeedback("Writing Layer Search...")
    if layerSearch != "None" and layerSearch != "":
        cssAddress += """
        <link rel="stylesheet" type="text/css" href="resources/horsey.min.css">
        <link rel="stylesheet" type="text/css" """
        cssAddress += """href="resources/ol3-search-layer.min.css">"""
        jsAddress += """
        <script src="http://cdn.polyfill.io/v2/polyfill.min.js?features="""
        jsAddress += """Element.prototype.classList,URL"></script>
        <script src="resources/horsey.min.js"></script>
        <script src="resources/ol3-search-layer.js"></script>"""
        searchVals = layerSearch.split(": ")
        layerSearch = u"""
    var searchLayer = new SearchLayer({{
      layer: lyr_{layer},
      colName: '{field}',
      zoom: 10,
      collapsed: true,
      map: map
    }});

    map.addControl(searchLayer);
    document.getElementsByClassName('search-layer')[0]
    .getElementsByTagName('button')[0].className +=
    ' fa fa-binoculars';
    """.format(layer=searchLayer, field=searchVals[1])
        controlCount = controlCount + 1
    else:
        layerSearch = ""
    feedback.completeStep()
    return (jsAddress, cssAddress, layerSearch, controlCount)


def writeScriptIncludes(layers, json, matchCRS):
    geojsonVars = ""
    wfsVars = ""
    styleVars = ""
    for count, (layer, encode2json) in enumerate(zip(layers, json)):
        vts = layer.customProperty("VectorTilesReader/vector_tile_url")
        sln = safeName(layer.name()) + "_" + str(count)
        if layer.type() == layer.VectorLayer:
            if layer.providerType() != "WFS" or encode2json:
                if vts is None:
                    geojsonVars += ('<script src="layers/%s"></script>' %
                                    (sln + ".js"))
            else:
                layerSource = layer.source()
                if ("retrictToRequestBBOX" in layerSource or
                        "restrictToRequestBBOX" in layerSource):
                    provider = layer.dataProvider()
                    uri = QgsDataSourceUri(provider.dataSourceUri())
                    wfsURL = uri.param("url")
                    wfsTypename = uri.param("typename")
                    wfsSRS = uri.param("srsname")
                    layerSource = wfsURL
                    layerSource += "?SERVICE=WFS&VERSION=1.0.0&"
                    layerSource += "REQUEST=GetFeature&TYPENAME="
                    layerSource += wfsTypename
                    layerSource += "&SRSNAME="
                    layerSource += wfsSRS
                if not matchCRS:
                    layerSource = re.sub(r'SRSNAME\=EPSG\:\d+',
                                         'SRSNAME=EPSG:3857',
                                         layerSource)
                layerSource += "&outputFormat=text%2Fjavascript&"
                layerSource += "format_options=callback%3A"
                layerSource += "get" + sln + "Json"
                wfsVars += ('<script src="%s"></script>' % layerSource)
            if vts is not None:
                sln = safeName(vts)
            styleVars += ('<script src="styles/%s_style.js">'
                          '</script>' % sln)
    return (geojsonVars, wfsVars, styleVars)
