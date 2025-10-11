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
    src = os.path.join(os.path.dirname(__file__), "openlayers")
    if not os.path.exists(dst):
        shutil.copytree(src,dst)
    feedback.completeStep()


def writeHTMLstart(settings, controlCount, osmb, feedback):
    feedback.showFeedback("Writing HTML...")
    jsAddress = """<script src="./resources/functions.js"></script>"""
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
        cssAddress += """href="resources/ol-search-layer.min.css">"""
        jsAddress += """
        <script src="resources/horsey.min.js"></script>
        <script src="resources/ol-search-layer.js"></script>"""
        searchVals = layerSearch.split(": ")
        layerSearch = u"""
var searchLayer = new SearchLayer({{
    layer: lyr_{layer},
    colName: '{field}',
    zoom: 10,
    collapsed: true,
    map: map,
    maxResults: 10,
}});
map.addControl(searchLayer);
document.getElementsByClassName('search-layer')[0].getElementsByTagName('button')[0].className += ' fa fa-binoculars';
document.getElementsByClassName('search-layer-input-search')[0].placeholder = 'Search feature ...';
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
                # Caso WFS
                provider = layer.dataProvider()
                uri = QgsDataSourceUri(provider.dataSourceUri())
                wfsURL = uri.param("url")
                wfsTypename = uri.param("typename")
                if not matchCRS:
                    wfsSRS = "EPSG:3857"
                else:
                    wfsSRS = uri.param("srsname") or "EPSG:3857"

                baseURL = (f"{wfsURL}?SERVICE=WFS&VERSION=1.0.0&"
                           f"REQUEST=GetFeature&TYPENAME={wfsTypename}&"
                           f"SRSNAME={wfsSRS}")

                wfsVars += '''
        <script>
            function fetchWFS%(layerName)sData(title, callback) {
                var url = "%(baseURL)s";

                function fetchWithFallback(u) {
                    return fetch(u)
                        .then(function (r) {
                            if (!r.ok) throw new Error("Bad response");
                            return r.text();
                        })
                        .catch(function () {
                            // Fallback AllOrigins
                            return fetch("https://api.allorigins.win/raw?url=" + encodeURIComponent(u))
                                .then(function (r) {
                                    if (!r.ok) throw new Error("Proxy failed");
                                    return r.text();
                                });
                        });
                }

                // Imposta un'icona di caricamento durante il fetch
                lyr_%(layerName)s.set('title', '<div class="roller-switcher" title="Fetching WFS data"></div> ' + title);
    
                fetchWithFallback(url)
                    .then(function (response) {
                        if (typeof callback === "function") {
                            lyr_%(layerName)s.set('title', title);
                            layerSwitcher.renderPanel();
                            callback(null, response); // Pass null as error
                        } else {
                            console.error("Callback not defined.");
                        }
                    })
                    .catch(function (error) {
                        if (typeof callback === "function") {
                            lyr_%(layerName)s.set('title', '<i class="fa-regular fa-triangle-exclamation" title="Error on fetch data"></i> ' + title);
                            layerSwitcher.renderPanel();
                            callback(error, null); // Pass the error
                        } else {
                            lyr_%(layerName)s.set('title', '<i class="fa-regular fa-triangle-exclamation" title="Error on fetch data"></i> ' + title);
                            layerSwitcher.renderPanel();
                            console.error("Error fetching %(layerName)s data:", error);
                        }
                    });
            }
        </script>
        ''' % {'layerName': sln, 'baseURL': baseURL}
            if vts is not None:
                sln = safeName(vts)
            styleVars += ('<script src="styles/%s_style.js">'
                          '</script>' % sln)
    return (geojsonVars, wfsVars, styleVars)
