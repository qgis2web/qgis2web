from math import floor
from qgis.core import *
# from qgis.utils import QGis
from utils import getRGBAColor, handleHiddenField


def getLayerStyle(layer, sln, markerFolder):
    renderer = layer.rendererV2()
    layer_alpha = layer.layerTransparency()
    style = ""
    if (isinstance(renderer, QgsSingleSymbolRendererV2) or
            isinstance(renderer, QgsRuleBasedRendererV2)):
        if isinstance(renderer, QgsRuleBasedRendererV2):
            symbol = renderer.rootRule().children()[0].symbol()
        else:
            symbol = renderer.symbol()
        style = """
        function style_%s() {
            return %s
        }""" % (sln, getSymbolAsStyle(symbol, markerFolder, layer_alpha, sln))
    elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        style = """
        function style_%s(feature) {
            switch(feature.properties['%s']) {""" % (sln, classAttr)
        for cat in renderer.categories():
            style += """
                case '%s':
                    return %s
                    break;""" % (cat.value(), getSymbolAsStyle(
                                    cat.symbol(), markerFolder,
                                    layer_alpha, sln))
        style += """
            }
        }"""
    elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        style = """
        function style_%s(feature) {""" % (sln)
        for ran in renderer.ranges():
            style += """
            if (feature.properties['%(a)s'] > %(l)f && feature.properties['%(a)s'] < %(u)f ) {
                return %(s)s
            }""" % {"a": classAttr, "l": ran.lowerValue(),
                             "u": ran.upperValue(), "s": getSymbolAsStyle(
                                    ran.symbol(), markerFolder,
                                    layer_alpha, sln)}
        style += """
        }"""
    else:
        style = ""
    return style


def getSymbolAsStyle(symbol, markerFolder, layer_transparency, sln):
    styles = []
    if layer_transparency == 0:
        alpha = symbol.alpha()
    else:
        alpha = 1-(layer_transparency / float(100))
    sl = symbol.symbolLayer(0)
    props = sl.properties()
    if isinstance(sl, QgsSimpleMarkerSymbolLayerV2):
        color = getRGBAColor(props["color"], alpha)
        borderColor = getRGBAColor(props["outline_color"], alpha)
        borderWidth = props["outline_width"]
        size = symbol.size() * 2
        style = getCircle(color, borderColor, borderWidth, size, props)
    elif isinstance(sl, QgsSvgMarkerSymbolLayerV2):
        path = os.path.join(markerFolder, os.path.basename(sl.path()))
        svg = xml.etree.ElementTree.parse(sl.path()).getroot()
        svgWidth = svg.attrib["width"]
        svgWidth = re.sub("px", "", svgWidth)
        svgHeight = svg.attrib["height"]
        svgHeight = re.sub("px", "", svgHeight)
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
        style = ("image: %s" %
                 getIcon("styles/" + os.path.basename(sl.path()),
                         sl.size(), svgWidth, svgHeight, rot))
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
    else:
        style = ""
    return """{
                pane: 'pane_%s',%s
            }""" % (sln, style)


def getCircle(color, borderColor, borderWidth, size, props):
    return ("""
                radius: %s,%s%s""" %
            (size,
             getStrokeStyle(borderColor, "", borderWidth, 0, 0),
             getFillStyle(color, props)))


def getIcon(path, size, svgWidth, svgHeight, rot):
    size = floor(float(size) * 3.8)
    anchor = size / 2
    scale = unicode(float(size)/float(svgWidth))
    return '''new ol.style.Icon({
                  imgSize: [%(w)s, %(h)s],
                  scale: %(scale)s,
                  anchor: [%(a)d, %(a)d],
                  anchorXUnits: "pixels",
                  anchorYUnits: "pixels",
                  rotation: %(rot)s,
                  src: "%(path)s"
            })''' % {"w": svgWidth, "h": svgHeight,
                     "scale": scale, "rot": rot,
                     "s": size, "a": anchor,
                     "path": path.replace("\\", "\\\\")}


def getStrokeStyle(color, dashed, width, linecap, linejoin):
    width = round(float(width) * 3.8, 0)
    dash = dashed.replace("dash", "10,5")
    dash = dash.replace("dot", "1,5")
    dash = dash.replace("solid", "")
    dash = dash.replace(" ", ",")
    if dash == "no":
        dash = ""
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
    strokeString = ("""
                color: %s,
                dashArray: '%s',""" %
                    (color, dash))
    strokeString += ("""
                lineCap: '%s',
                lineJoin: '%s',
                weight: %d,""" %
                     (capString, joinString, width))
    return strokeString


def getFillStyle(color, props):
    try:
        if props["style"] == "no":
            return ""
    except:
        pass
    return """
                fillColor: %s,""" % color
