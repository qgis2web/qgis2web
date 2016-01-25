import re
import os
import time
import tempfile
from qgis.core import *
import processing
from utils import writeTmpLayer


def writeJSONLayer(i, eachPopup, precision, tmpFileName, exp_crs,
                   layerFileName, safeLayerName, minify):
    cleanedLayer = writeTmpLayer(i, eachPopup)
    writer = QgsVectorFileWriter
    options = "COORDINATE_PRECISION=" + unicode(precision)
    writer.writeAsVectorFormat(cleanedLayer, tmpFileName, 'utf-8',
                               exp_crs, 'GeoJson', 0,
                               layerOptions=[options])

    with open(layerFileName, "w") as f2:
        f2.write("var json_" + unicode(safeLayerName) + "=")
        with open(tmpFileName, "r") as tmpFile:
            for line in tmpFile:
                if minify:
                    line = line.strip("\n\t ")
                    line = removeSpaces(line)
                f2.write(line)
        os.remove(tmpFileName)
        f2.close


def writeRasterLayer(i, safeLayerName, dataPath):
    print "Raster type: " + unicode(i.rasterType())
    name_ts = safeLayerName + unicode(time.time())
    pipelayer = i
    pipeextent = pipelayer.extent()
    pipewidth, pipeheight = (pipelayer.width(),
                             pipelayer.height())
    piperenderer = pipelayer.renderer()
    pipeprovider = pipelayer.dataProvider()
    crs = pipelayer.crs().toWkt()
    pipe = QgsRasterPipe()
    pipe.set(pipeprovider.clone())
    pipe.set(piperenderer.clone())
    pipedFile = os.path.join(tempfile.gettempdir(),
                             name_ts + '_pipe.tif')
    print "pipedFile: " + pipedFile
    file_writer = QgsRasterFileWriter(pipedFile)
    file_writer.writeRaster(pipe,
                            pipewidth,
                            pipeheight,
                            pipeextent,
                            pipelayer.crs())

    in_raster = pipedFile
    print "in_raster: " + in_raster
    prov_raster = os.path.join(tempfile.gettempdir(),
                               'json_' + name_ts +
                               '_prov.tif')
    print "prov_raster: " + prov_raster
    out_raster = dataPath + '.png'
    print "out_raster: " + out_raster
    crsSrc = i.crs()
    crsDest = QgsCoordinateReferenceSystem(4326)
    xform = QgsCoordinateTransform(crsSrc, crsDest)
    extentRep = xform.transform(i.extent())
    extentRepNew = ','.join([unicode(extentRep.xMinimum()),
                             unicode(extentRep.xMaximum()),
                             unicode(extentRep.yMinimum()),
                             unicode(extentRep.yMaximum())])
    processing.runalg("gdalogr:warpreproject", in_raster,
                      i.crs().authid(), "EPSG:4326", "", 0, 1,
                      5, 2, 75, 6, 1, False, 0, False, "",
                      prov_raster)
    del in_raster
    del pipedFile
    os.remove(os.path.join(tempfile.gettempdir(),
                           name_ts + '_pipe.tif'))
    processing.runalg("gdalogr:translate", prov_raster, 100,
                      True, "", 0, "", extentRepNew, False, 0,
                      0, 75, 6, 1, False, 0, False, "",
                      out_raster)
    del prov_raster
    os.remove(os.path.join(tempfile.gettempdir(),
                           'json_' + name_ts + '_prov.tif'))


def buildPointWFS(pointStyleLabel, layerName, layerSource, categoryStr,
                  cluster_set, cluster_num, visible):
    scriptTag = re.sub('SRSNAME\=EPSG\:\d+', 'SRSNAME=EPSG:4326', layerSource)
    scriptTag += "&outputFormat=text%2Fjavascript&format_options=callback%3A"
    scriptTag += "get" + layerName + "Json"
    new_obj = pointStyleLabel + categoryStr + """
        var json_{layerName}JSON;
        json_{layerName}JSON = L.geoJson(null, {{
            pointToLayer: doPointToLayer{layerName},
            onEachFeature: pop_{layerName}
        }});
        layerControl.addOverlay(json_""".format(layerName=layerName)
    new_obj += "{layerName}JSON, '{layerName}');".format(layerName=layerName)
    if cluster_set:
        new_obj += """
        var cluster_group{layerName}JSON = """.format(layerName=layerName)
        new_obj += "new L.MarkerClusterGroup({showCoverageOnHover: false});"
        new_obj += """
        layerOrder[layerOrder.length] = cluster_group"""
        new_obj += "{layerName}JSON;".format(layerName=layerName)
    else:
        new_obj += """
        feature_group.addLayer(json_{layerName}JSON);
        layerOrder[layerOrder.length] = json_{layerName}JSON;""".format(
                layerName=layerName)
    new_obj += """
        function get{layerName}Json(geojson) {{
            json_{layerName}""".format(layerName=layerName)
    new_obj += "JSON.addData(geojson);"
    if visible:
        new_obj += """
            stackLayers();"""
    if cluster_set:
        new_obj += """
                cluster_group{layerName}JSON.add""".format(layerName=layerName)
        new_obj += "Layer(json_{layerName}JSON);".format(layerName=layerName)
        cluster_num += 1
    new_obj += """
        };"""
    return new_obj, scriptTag, cluster_num


def buildNonPointJSON(categoryStr, safeName, usedFields):
    if usedFields != 0:
        new_obj = categoryStr + """
            var json_{safeName}JSON = new L.geoJson(json_{safeName}, {{
                onEachFeature: pop_{safeName},
                style: doStyle{safeName}
            }});
            layerOrder[layerOrder.length]""".format(safeName=safeName)
        new_obj += " = json_{safeName}JSON;".format(safeName=safeName)
    else:
        new_obj = categoryStr + """
            var json_{safeName}JSON = new L.geoJson(json_{safeName}, {{
                style: doStyle{safeName}
            }});
            layerOrder[layerOrder.length] = """.format(safeName=safeName)
        new_obj += "json_{safeName}JSON;".format(safeName=safeName)
    return new_obj


def buildNonPointWFS(layerName, layerSource, categoryStr,
                     stylestr, visible):
    scriptTag = re.sub('SRSNAME\=EPSG\:\d+', 'SRSNAME=EPSG:4326', layerSource)
    scriptTag += "&outputFormat=text%2Fjavascript&format_options=callback"
    scriptTag += "%3Aget{layerName}Json".format(layerName=layerName)
    new_obj = categoryStr + """
        var json_{layerName}JSON;
        json_{layerName}JSON = L.geoJson(null, {{{stylestr},
            onEachFeature: pop_{layerName}
        }});""".format(layerName=layerName, stylestr=stylestr)
    new_obj += """
        layerOrder[layerOrder.length] = json_{layerName}JSON;
        feature_group.addLayer(json_{layerName}JSON);
        layerControl.addOverlay(json_""".format(layerName=layerName)
    new_obj += "{layerName}JSON, '{layerName}');".format(layerName=layerName)
    new_obj += """
        function get{layerName}Json(geojson) {{
            json_{layerName}""".format(layerName=layerName)
    new_obj += "JSON.addData(geojson);"
    if visible:
        new_obj += """
            stackLayers();"""
    new_obj += """
        };"""
    return new_obj, scriptTag


def stackLayers(layerName, visible):
    if visible:
        return """
        layerOrder[layerOrder.length] = json_{layerName}JSON;
        stackLayers();""".format(layerName=layerName)
    else:
        return ""
