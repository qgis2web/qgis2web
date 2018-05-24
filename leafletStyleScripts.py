import os
import shutil
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
        slCount = symbol.symbolLayerCount()
        if slCount < 1:
            slCount = 1
        for sl in xrange(slCount):
            (styleCode, markerType, useMapUnits,
             pattern) = getSymbolAsStyle(symbol, markerFolder,
                                         layer_alpha, sln, sl, 0)
            style += pattern
            style += """
        function style_%s_%s() {
            return %s
        }""" % (sln, sl, styleCode)
    elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        symbol = renderer.categories()[0].symbol()
        slCount = symbol.symbolLayerCount()
        patterns = ""
        if slCount < 1:
            slCount = 1
        for sl in xrange(slCount):
            style += """
        function style_%s_%s(feature) {
            switch(String(feature.properties['%s'])) {""" % (sln, sl,
                                                             classAttr)
            for cnt, cat in enumerate(renderer.categories()):
                (styleCode, markerType, useMapUnits,
                 pattern) = getSymbolAsStyle(cat.symbol(), markerFolder,
                                             layer_alpha, sln, sl, cnt)
                patterns += pattern
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
            style = patterns + style + """
            }
        }"""
    elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        symbol = renderer.ranges()[0].symbol()
        slCount = symbol.symbolLayerCount()
        patterns = ""
        if slCount < 1:
            slCount = 1
        for sl in xrange(slCount):
            style += """
        function style_%s_%s(feature) {""" % (sln, sl)
            for cnt, ran in enumerate(renderer.ranges()):
                (styleCode, markerType, useMapUnits,
                 pattern) = getSymbolAsStyle(ran.symbol(), markerFolder,
                                             layer_alpha, sln, sl, cnt)
                patterns += pattern
                style += """
            if (feature.properties['%(a)s'] >= %(l)f """
                style += """&& feature.properties['%(a)s'] <= %(u)f ) {
                return %(s)s
            }"""
                style = style % {"a": classAttr, "l": ran.lowerValue(),
                                 "u": ran.upperValue(),
                                 "s": styleCode}
            style = patterns + style + """
        }"""
    elif isinstance(renderer, QgsRuleBasedRendererV2):
        symbol = renderer.rootRule().children()[0].symbol()
        slCount = symbol.symbolLayerCount()
        if slCount < 1:
            slCount = 1
        for sl in xrange(slCount):
            template = """
        %s
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
            patterns = ""
            for count, rule in enumerate(rules):
                if rule.symbol().symbolLayer(sl) is not None:
                    (styleCode, markerType, useMapUnits,
                     pattern) = getSymbolAsStyle(rule.symbol(), markerFolder,
                                                 layer_alpha, sln, sl, count)
                    patterns += pattern
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
            if js == "":
                js = """
                if (false) {}"""
            style += template % (patterns, sln, js, elsejs)
    else:
        useMapUnits = False
        style = ""
    if markerType == "shapeMarker":
        useShapes = True
    return style, markerType, useMapUnits, useShapes


def getSymbolAsStyle(symbol, markerFolder, layer_transparency, sln, sl, cat):
    markerType = None
    pattern = ""
    styles = []
    if layer_transparency == 0:
        alpha = symbol.alpha()
    else:
        alpha = 1 - (layer_transparency / float(100))
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
        borderUnits = props["outline_width_unit"]
        lineStyle = props["outline_style"]
        sizeUnits = props["size_unit"]
        size = sl.size()
        if sizeUnits != "MapUnit":
            size = size * 2
        shape = 8
        try:
            shape = sl.shape()
        except:
            try:
                shape = sl.name()
            except:
                pass
        style, useMapUnits = getMarker(color, borderColor, borderWidth,
                                       borderUnits, size, sizeUnits, props,
                                       lineStyle, shape)
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
        useMapUnits = False
    elif isinstance(sl, QgsSimpleLineSymbolLayerV2):
        color = getRGBAColor(props["line_color"], alpha)
        line_width = props["line_width"]
        line_style = props["line_style"]
        line_units = props["line_width_unit"]

        lineCap = sl.penCapStyle()
        lineJoin = sl.penJoinStyle()

        style, useMapUnits = getStrokeStyle(color, line_style, line_width,
                                            line_units, lineCap, lineJoin)
        style += """
                fillOpacity: 0,"""
    elif isinstance(sl, QgsSimpleFillSymbolLayerV2):
        fillColor = getRGBAColor(props["color"], alpha)

        borderColor = getRGBAColor(props["outline_color"], alpha)
        borderStyle = props["outline_style"]
        borderWidth = props["outline_width"]
        line_units = props["outline_width_unit"]

        try:
            lineCap = sl.penCapStyle()
            lineJoin = sl.penJoinStyle()
        except:
            lineCap = 0
            lineJoin = 0

        strokeStyle, useMapUnits = getStrokeStyle(borderColor, borderStyle,
                                                  borderWidth, line_units,
                                                  lineCap, lineJoin)

        style = ('''%s %s''' %
                 (strokeStyle, getFillStyle(fillColor, props)))
    elif isinstance(sl, QgsLinePatternFillSymbolLayer):
        weight = sl.subSymbol().width()
        spaceWeight = sl.distance()
        color = sl.color().name()
        angle = 360 - sl.lineAngle()
        pattern = """
        var pattern_%s_%d_%d = new L.StripePattern({
            weight: %s,
            spaceWeight: %s,
            color: '%s',
            opacity: %s,
            spaceOpacity: 0,
            angle: %d
        });
        pattern_%s_%d_%d.addTo(map);""" % (sln, slc, cat, weight, spaceWeight,
                                           color, alpha, angle, sln, slc, cat)
        style = """
                stroke: false,
                fillOpacity: 1,
                fillPattern: pattern_%s_%d_%d""" % (sln, slc, cat)
        useMapUnits = False
    else:
        markerType = "circleMarker"
        style = ""
        useMapUnits = False
    return ("""{
                pane: 'pane_%s',%s
            }""" % (sln, style), markerType, useMapUnits, pattern)


def getMarker(color, borderColor, borderWidth, borderUnits, size, sizeUnits,
              props, lineStyle, shape):
    useMapUnits = False
    strokeStyle, useMapUnits = getStrokeStyle(borderColor, lineStyle,
                                              borderWidth, borderUnits, 0, 0)
    if sizeUnits == "MapUnit":
        useMapUnits = True
        size = "geoStyle(%s)" % size
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
                radius: %s,%s%s""" % (markerShape, size, strokeStyle,
                                      getFillStyle(color, props)),
            useMapUnits)


def getIcon(path, svgSize):
    return '''L.icon({
            iconUrl: '%(path)s',
            iconSize: [%(s)s, %(s)s]
        }),''' % {"s": svgSize, "path": path.replace("\\", "\\\\")}


def getStrokeStyle(color, dashed, width, units, linecap, linejoin):
    useMapUnits = False
    if dashed != "no":
        width = round(float(width) * 3.8, 0)
        if width == 0:
            width = 1
        if units == "MapUnit":
            useMapUnits = True
            width = "geoStyle(%s)" % width
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
    return strokeString, useMapUnits


def getFillStyle(color, props):
    try:
        if props["style"] == "no":
            return """
                fillOpacity: 0,"""
    except:
        pass
    return """
                fill: true,
                fillOpacity: 1,
                fillColor: %s,""" % color
