import os
import shutil
from qgis.core import (QgsSingleSymbolRenderer,
                       QgsCategorizedSymbolRenderer,
                       QgsGraduatedSymbolRenderer,
                       QgsRuleBasedRenderer,
                       QgsLineSymbol,
                       QgsFillSymbol,
                       QgsSimpleMarkerSymbolLayer,
                       QgsSimpleLineSymbolLayer,
                       QgsSimpleFillSymbolLayer,
                       QgsLinePatternFillSymbolLayer,
                       QgsSvgMarkerSymbolLayer)
from qgis2web.exp2js import compile_to_file
from qgis2web.utils import getRGBAColor, handleHiddenField

COLOR = 1
NUMERIC = 2


def getLayerStyle(layer, sln, markerFolder, outputProjectFilename, useShapes):
    markerType = None
    useMapUnits = False
    renderer = layer.renderer()
    layer_alpha = layer.opacity()
    layout = ""
    paint = ""
    if isinstance(renderer, QgsSingleSymbolRenderer):
        symbol = renderer.symbol()
        slCount = symbol.symbolLayerCount()
        if slCount < 1:
            slCount = 1
        for sl in range(slCount):
            (layoutCode, paintCode, markerType, useMapUnits,
             pattern) = getSymbolAsStyle(symbol, markerFolder,
                                         layer_alpha, sln, sl, useMapUnits,
                                         layer, renderer)
            layout = layoutCode
            paint = paintCode
    elif isinstance(renderer, QgsCategorizedSymbolRenderer):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        symbol = renderer.categories()[0].symbol()
        slCount = symbol.symbolLayerCount()
        patterns = ""
        if slCount < 1:
            slCount = 1
        for sl in range(slCount):
            layout += """
        function style_%s_%s(feature) {
            switch(String(feature.properties['%s'])) {""" % (sln, sl,
                                                             classAttr)
            for cat in renderer.categories():
                (layoutCode, paintCode, markerType, useMapUnits,
                 pattern) = getSymbolAsStyle(cat.symbol(), markerFolder,
                                             layer_alpha, sln, sl, useMapUnits,
                                             layer, renderer)
                patterns += pattern
                if (cat.value() is not None and cat.value() != ""):
                    layout += """
                case '%s':""" % unicode(cat.value()).replace("'", "\\'")
                else:
                    layout += """
                default:"""
                layout += """
                    return %s
                    break;""" % layoutCode
            layout = patterns + layout + """
            }
        }"""
        layout = layoutCode
        paint = paintCode
    elif isinstance(renderer, QgsGraduatedSymbolRenderer):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        symbol = renderer.ranges()[0].symbol()
        slCount = symbol.symbolLayerCount()
        patterns = ""
        if slCount < 1:
            slCount = 1
        for sl in range(slCount):
            style += """
        function style_%s_%s(feature) {""" % (sln, sl)
            for ran in renderer.ranges():
                (layoutCode, paintCode, markerType, useMapUnits,
                 pattern) = getSymbolAsStyle(ran.symbol(), markerFolder,
                                             layer_alpha, sln, sl, useMapUnits,
                                             layer, renderer)
                patterns += pattern
                layout += """
            if (feature.properties['%(a)s'] >= %(l)f """
                layout += """&& feature.properties['%(a)s'] <= %(u)f ) {
                return %(s)s
            }"""
                layout = laout % {"a": classAttr, "l": ran.lowerValue(),
                                 "u": ran.upperValue(),
                                 "s": styleCode}
            layout = patterns + style + """
        }"""
        layout = ""
        paint = ""
    elif isinstance(renderer, QgsRuleBasedRenderer):
        symbol = renderer.rootRule().children()[0].symbol()
        slCount = symbol.symbolLayerCount()
        patterns = ""
        if slCount < 1:
            slCount = 1
        for sl in range(slCount):
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
            for count, rule in enumerate(rules):
                if rule.symbol().symbolLayer(sl) is not None:
                    (layoutCode, paintCode, markerType, useMapUnits,
                     pattern) = getSymbolAsStyle(rule.symbol(), markerFolder,
                                                 layer_alpha, sln, sl,
                                                 useMapUnits, layer, renderer)
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
            layout += template % (patterns, sln, js, elsejs)
        layout = ""
        paint = ""
    else:
        useMapUnits = False
        layout = ""
        paint = ""
    if markerType == "shapeMarker":
        useShapes = True
    return layout, paint, markerType, useMapUnits, useShapes


def getSymbolAsStyle(symbol, markerFolder, layer_transparency, sln, sl,
                     useMapUnits, layer, renderer):
    markerType = None
    pattern = ""
    styles = []
    if layer_transparency == 0:
        alpha = symbol.alpha()
    else:
        alpha = layer_transparency
    slc = sl
    sl = symbol.symbolLayer(sl)
    try:
        props = sl.properties()
    except:
        props = {}
    if isinstance(sl, QgsSimpleMarkerSymbolLayer):
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
                                       lineStyle, shape, renderer)
        try:
            if shape == 8 or shape == "circle":
                markerType = "circleMarker"
            else:
                markerType = "shapeMarker"
        except:
            markerType = "circleMarker"
        labelling = layer.labeling()
        if labelling is not None:
            palyr = labelling.settings()
            if palyr and palyr.fieldName and palyr.fieldName != "":
                layout = """
                "text-field": "{%s}",
                "text-font": ["Open Sans Regular"]""" % palyr.fieldName
        else:
            layout = ""
        paint = ""
    elif isinstance(sl, QgsSvgMarkerSymbolLayer):
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
        layout = ""
        paint = ""
    elif isinstance(sl, QgsSimpleLineSymbolLayer):
        color = getRGBAColor(props["line_color"], alpha)
        line_width = props["line_width"]
        line_style = props["line_style"]
        line_units = props["line_width_unit"]

        lineCap = sl.penCapStyle()
        lineJoin = sl.penJoinStyle()

        layout = ""
        paint, useMapUnits = getStrokeStyle(color, line_style, line_width,
                                            line_units, lineCap, lineJoin,
                                            useMapUnits, props, renderer)
    elif isinstance(sl, QgsSimpleFillSymbolLayer):
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
                                                  lineCap, lineJoin,
                                                  useMapUnits, props, renderer)

        layout = ""
        paint = getFillStyle(renderer, fillColor, props)
    elif isinstance(sl, QgsLinePatternFillSymbolLayer):
        weight = sl.subSymbol().width()
        spaceWeight = sl.distance()
        color = sl.color().name()
        angle = 360 - sl.lineAngle()
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
        paint = """
                stroke: false,
                fillOpacity: 1,
                fillPattern: pattern_%s_%d""" % (sln, slc)
        layout = ""
        paint = ""
    else:
        markerType = "circleMarker"
        layout = ""
        paint = ""
        useMapUnits = False
    return (layout, paint, markerType, useMapUnits, pattern)


def getMarker(color, borderColor, borderWidth, borderUnits, size, sizeUnits,
              props, lineStyle, shape, renderer):
    useMapUnits = False
    strokeStyle, useMapUnits = getStrokeStyle(borderColor, lineStyle,
                                              borderWidth, borderUnits, 0, 0,
                                              useMapUnits, props, renderer)
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
                                      getFillStyle(renderer, color, props)),
            useMapUnits)


def getIcon(path, svgSize):
    return '''L.icon({
            iconUrl: '%(path)s',
            iconSize: [%(s)s, %(s)s]
        }),''' % {"s": svgSize, "path": path.replace("\\", "\\\\")}


def getStrokeStyle(color, dashed, width, units, linecap, linejoin,
                   useMapUnits, props, renderer):
    if isinstance(renderer, QgsSingleSymbolRenderer):
        if isinstance(renderer.symbol().symbolLayer(0),
                      QgsSimpleFillSymbolLayer):
            color = getColor(props["outline_color"])
            line_width = props["outline_width"]
        elif isinstance(renderer.symbol().symbolLayer(0),
                        QgsSimpleLineSymbolLayer):
            color = getColor(props["line_color"])
            line_width = props["line_width"]
        lineColor = color
        lineWidth = width
    elif isinstance(renderer, QgsCategorizedSymbolRenderer):
        if isinstance(renderer.categories()[0].symbol(), QgsFillSymbol):
            colorProp = "outline_color"
            widthProp = "outline_width"
        elif isinstance(renderer.categories()[0].symbol(), QgsLineSymbol):
            colorProp = "line_color"
            widthProp = "line_width"
        classAttr = renderer.classAttribute()
        categories = renderer.categories()
        lineColor = getCategorizedValues(colorProp, classAttr, categories,
                                         COLOR)
        lineWidth = getCategorizedValues(widthProp, classAttr, categories,
                                      NUMERIC)
    strokeString = """
            "line-color": %s,
            "line-width": %s""" % (lineColor, lineWidth)
    return strokeString, useMapUnits


def getFillStyle(renderer, color, props):
    try:
        if props["style"] == "no":
            return ""
    except:
        pass

    if isinstance(renderer, QgsSingleSymbolRenderer):
        symbol = renderer.symbol()
        fillcolor = symbol.color().name()
        fill = '"%s"' % fillcolor
        strokeColor = symbol.symbolLayer(0).strokeColor().name()
        stroke = '"%s"' % strokeColor

    elif isinstance(renderer, QgsCategorizedSymbolRenderer):
        classAttr = renderer.classAttribute()
        categories = renderer.categories()
        fill = getCategorizedValues("color", classAttr, categories, COLOR)
        stroke = getCategorizedValues("outline_color", classAttr, categories,
                                      COLOR)
    return """
                "fill-color": %s,
                "fill-outline-color": %s""" % (fill, stroke)


def getCategorizedValues(property, classAttr, categories, type):
    if type == COLOR:
        defaultVal = '["rgba", 0,0,0,0]'
    elif type == NUMERIC:
        defaultVal = 0
    catStyles = []
    for cat in categories:
        value = cat.value()
        symbol = cat.symbol()
        props = symbol.symbolLayer(0).properties()
        if value:
            catStyles.append('"%s"' % unicode(value).replace('"', '\\"'))
        val = props[property]
        if type == COLOR:
            typedVal = getColor(val)
        elif type == NUMERIC:
            typedVal = val
        if value:
            catStyles.append(typedVal)
        else:
            defaultVal = typedVal
    style = """[
                "match",
                [
                    "get",
                    "%s"
                ],
                %s,
                %s
            ]""" % (classAttr, ",".join(catStyles), defaultVal)
    return style


def getColor(color):
    r, g, b, a = color.split(",")
    a = (float(a) / 255)
    return '["rgba", %s]' % ",".join([r, g, b, str(a)])
