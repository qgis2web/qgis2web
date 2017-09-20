import os
import shutil
import re
from math import floor
import xml.etree.ElementTree
from PyQt4.QtCore import QPyNullVariant
from qgis.core import (QgsSingleSymbolRendererV2,
                       QgsCategorizedSymbolRendererV2,
                       QgsGraduatedSymbolRendererV2,
                       QgsRuleBasedRendererV2,
                       QgsSimpleMarkerSymbolLayerV2,
                       QgsSimpleLineSymbolLayerV2,
                       QgsSimpleFillSymbolLayerV2,
                       QgsLinePatternFillSymbolLayer,
                       QgsSvgMarkerSymbolLayerV2)
from exp2js import compile_to_file
from utils import getRGBAColor, handleHiddenField


def getLayerStyle(layer, sln, markerFolder, outputProjectFilename, useShapes):
    markerType = None
    renderer = layer.rendererV2()
    layer_alpha = layer.layerTransparency()
    style = ""
    if isinstance(renderer, QgsSingleSymbolRendererV2):
        symbol = renderer.symbol()
        for sl in xrange(symbol.symbolLayerCount()):
            (styleCode, markerType,
             pattern) = getSymbolAsStyle(symbol, markerFolder,
                                         layer_alpha, sln, sl)
            style += pattern
            style += """
        function style_%s_%s() {
            return %s
        }""" % (sln, sl, styleCode)
    elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        symbol = renderer.categories()[0].symbol()
        for sl in xrange(symbol.symbolLayerCount()):
            style += """
        function style_%s_%s(feature) {
            switch(feature.properties['%s'].toString()) {""" % (sln, sl,
                                                                classAttr)
            for cat in renderer.categories():
                (styleCode, markerType,
                 pattern) = getSymbolAsStyle(cat.symbol(), markerFolder,
                                             layer_alpha, sln, sl)
                if (cat.value() is not None and cat.value() != "" and
                        not isinstance(cat.value(), QPyNullVariant)):
                    style += """
                case '%s':""" % unicode(cat.value()).replace("'", "\\'")
                else:
                    style += """
                default:"""
                style += """
                    return %s
                    break;""" % styleCode
            style += """
            }
        }"""
    elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        symbol = renderer.ranges()[0].symbol()
        for sl in xrange(symbol.symbolLayerCount()):
            style += """
        function style_%s_%s(feature) {""" % (sln, sl)
            for ran in renderer.ranges():
                (styleCode, markerType,
                 pattern) = getSymbolAsStyle(ran.symbol(), markerFolder,
                                             layer_alpha, sln, sl)
                style += """
            if (feature.properties['%(a)s'] >= %(l)f """
                style += """&& feature.properties['%(a)s'] <= %(u)f ) {
                return %(s)s
            }"""
                style = style % {"a": classAttr, "l": ran.lowerValue(),
                                 "u": ran.upperValue(),
                                 "s": styleCode}
            style += """
        }"""
    elif isinstance(renderer, QgsRuleBasedRendererV2):
        symbol = renderer.rootRule().children()[0].symbol()
        for sl in xrange(symbol.symbolLayerCount()):
            template = """
        function style_%s_{sl}(feature) {{
            var context = {{
                feature: feature,
                variables: {{}}
            }};
            // Start of if blocks and style check logic
            %s
            else {{
                return %s;
            }}
        }}
        """.format(sl=sl)
            elsejs = "{fill: false, stroke: false}"
            js = ""
            root_rule = renderer.rootRule()
            rules = root_rule.children()
            expFile = os.path.join(outputProjectFilename, "js",
                                   "qgis2web_expressions.js")
            ifelse = "if"
            for count, rule in enumerate(rules):
                if rule.symbol().symbolLayer(sl) is not None:
                    (styleCode, markerType,
                     pattern) = getSymbolAsStyle(rule.symbol(), markerFolder,
                                                 layer_alpha, sln, sl)
                    name = "".join((sln, "rule", unicode(count)))
                    exp = rule.filterExpression()
                    if rule.isElse():
                        elsejs = styleCode
                        continue
                    name = compile_to_file(exp, name, "Leaflet", expFile)
                    js += """
                %s (%s(context)) {
                  return %s;
                }
                """ % (ifelse, name, styleCode)
                    js = js.strip()
                    ifelse = "else if"
            style += template % (sln, js, elsejs)
    else:
        style = ""
    if markerType == "shapeMarker":
        useShapes = True
    return style, markerType, useShapes


def getSymbolAsStyle(symbol, markerFolder, layer_transparency, sln, sl):
    markerType = None
    pattern = ""
    styles = []
    if layer_transparency == 0:
        alpha = symbol.alpha()
    else:
        alpha = 1-(layer_transparency / float(100))
    slc = sl
    sl = symbol.symbolLayer(sl)
    try:
        props = sl.properties()
    except:
        props = {}
    if isinstance(sl, QgsSimpleMarkerSymbolLayerV2):
        color = getRGBAColor(props["color"], alpha)
        borderColor = getRGBAColor(props["outline_color"], alpha)
        borderWidth = props["outline_width"]
        lineStyle = props["outline_style"]
        size = sl.size() * 2
        shape = 8
        try:
            shape = sl.shape()
        except:
            try:
                shape = sl.name()
            except:
                pass
        style = getMarker(color, borderColor, borderWidth,
                          size, props, lineStyle, shape)
        try:
            if shape == 8 or shape == "circle":
                markerType = "circleMarker"
            else:
                markerType = "shapeMarker"
        except:
            markerType = "circleMarker"
    elif isinstance(sl, QgsSvgMarkerSymbolLayerV2):
        path = os.path.join(markerFolder, os.path.basename(sl.path()))
        svgSize = sl.size() * 3.8
        if symbol.dataDefinedAngle().isActive():
            if symbol.dataDefinedAngle().useExpression():
                rot = "0"
            else:
                rot = "feature.get("
                rot += symbol.dataDefinedAngle().expressionOrField()
                rot += ") * 0.0174533"
        else:
            rot = unicode(sl.angle() * 0.0174533)
        shutil.copy(sl.path(), path)
        style = """
        rotationAngle: %s,
        rotationOrigin: 'center center',
        icon: %s""" % (rot, getIcon("markers/" + os.path.basename(sl.path()),
                                    svgSize))
        markerType = "marker"
    elif isinstance(sl, QgsSimpleLineSymbolLayerV2):

        # Check for old version
        if 'color' in props:
            color = getRGBAColor(props["color"], alpha)
        else:
            color = getRGBAColor(props["line_color"], alpha)

        if 'width' in props:
            line_width = props["width"]
        else:
            line_width = props["line_width"]

        if 'penstyle' in props:
            line_style = props["penstyle"]
        else:
            line_style = props["line_style"]

        lineCap = sl.penCapStyle()
        lineJoin = sl.penJoinStyle()

        style = getStrokeStyle(color, line_style, line_width,
                               lineCap, lineJoin)
        style += """
                fillOpacity: 0,"""
    elif isinstance(sl, QgsSimpleFillSymbolLayerV2):
        fillColor = getRGBAColor(props["color"], alpha)

        # for old version
        if 'color_border' in props:
            borderColor = getRGBAColor(props["color_border"], alpha)
        else:
            borderColor = getRGBAColor(props["outline_color"], alpha)

        if 'style_border' in props:
            borderStyle = props["style_border"]
        else:
            borderStyle = props["outline_style"]

        if 'width_border' in props:
            borderWidth = props["width_border"]
        else:
            borderWidth = props["outline_width"]

        try:
            lineCap = sl.penCapStyle()
            lineJoin = sl.penJoinStyle()
        except:
            lineCap = 0
            lineJoin = 0

        style = ('''%s %s''' %
                 (getStrokeStyle(borderColor, borderStyle, borderWidth,
                                 lineCap, lineJoin),
                  getFillStyle(fillColor, props)))
    elif isinstance(sl, QgsLinePatternFillSymbolLayer):
        weight = props["line_width"]
        spaceWeight = props["distance"]
        colors = props["color"].split(",")
        r = int(colors[0])
        g = int(colors[1])
        b = int(colors[2])
        color = '#%02x%02x%02x' % (r, g, b)
        angle = 360 - int(props["angle"])
        pattern = """
            var pattern_%s_%d = new L.StripePattern({
                weight: %s,
                spaceWeight: %s,
                color: '%s',
                opacity: %s,
                spaceOpacity: 0,
                angle: %d
            });
            pattern_%s_%d.addTo(map);""" % (sln, slc, weight, spaceWeight,
                                            color, alpha, angle, sln, slc)
        style = """
                stroke: false,
                fillPattern: pattern_%s_%d""" % (sln, slc)
    else:
        markerType = "circleMarker"
        style = ""
    return ("""{
                pane: 'pane_%s',%s
            }""" % (sln, style), markerType, pattern)


def getMarker(color, borderColor, borderWidth, size, props, lineStyle, shape):
    if shape == 0 or shape == "square":
        markerShape = "shape: 'square',"
    elif shape == 1 or shape == "diamond":
        markerShape = "shape: 'diamond',"
    elif shape == 4 or shape == "triangle":
        markerShape = "shape: 'triangle',"
    elif shape == 11 or shape == "cross2":
        markerShape = "shape: 'x',"
    else:
        markerShape = ""
    return ("""
                %s
                radius: %s,%s%s""" %
            (markerShape, size,
             getStrokeStyle(borderColor, lineStyle, borderWidth, 0, 0),
             getFillStyle(color, props)))


def getIcon(path, svgSize):
    return '''L.icon({
            iconUrl: '%(path)s',
            iconSize: [%(s)s, %(s)s]
        }),''' % {"s": svgSize, "path": path.replace("\\", "\\\\")}


def getStrokeStyle(color, dashed, width, linecap, linejoin):
    if dashed != "no":
        width = round(float(width) * 3.8, 0)
        if width == 0:
            width = 1
        dash = dashed.replace("dash", "10,5")
        dash = dash.replace("dot", "1,5")
        dash = dash.replace("solid", "")
        dash = dash.replace(" ", ",")
        capString = "round"
        if linecap == 0:
            capString = "butt"
        if linecap == 16:
            capString = "square"
        joinString = "round"
        if linejoin == 0:
            joinString = "miter"
        if linejoin == 64:
            joinString = "bevel"
        strokeString = """
                opacity: 1,
                color: %s,
                dashArray: '%s',""" % (color, dash)
        strokeString += """
                lineCap: '%s',
                lineJoin: '%s',
                weight: %s,""" % (capString, joinString, width)
    else:
        strokeString = """
                stroke: false,"""
    return strokeString


def getFillStyle(color, props):
    try:
        if props["style"] == "no":
            return """
                fillOpacity: 0,"""
    except:
        pass
    return """
                fillOpacity: 1,
                fillColor: %s,""" % color
