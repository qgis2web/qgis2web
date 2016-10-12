# from qgis.core import *
# from qgis.utils import QGis


def getLayerStyle(layer, sln):
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
        function style_%s(feature) {
            return %s;
        }""" % sln, getSymbolAsStyle(symbol, layer_alpha)
    elif isinstance(renderer, QgsCategorizedSymbolRendererV2):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        style = """
        function style_%s(feature) {
            switch(feature.properties['%s']) {""" % sln, classAttr
        for cat in renderer.categories():
            style += """
                case '%s':
                    return %s;
                    break;""" % (cat.value(), getSymbolAsStyle(
                                    cat.symbol(), layer_alpha))
        style += """
            }
        };"""
    elif isinstance(renderer, QgsGraduatedSymbolRendererV2):
        classAttr = handleHiddenField(layer, renderer.classAttribute())
        style = """
        function style_%s(feature) {
            switch(feature.properties['%s']) {""" % sln, classAttr
        for ran in renderer.ranges():
            style += """
            if (feature.properties['%(a)s'] > %(l)f && feature.properties['%(a)s'] < %(u)f ) {
                return %(s)s;
                break;""" % {"s": classAttr, "l": ran.lowerValue(),
                             "u": ran.upperValue(), "s": getSymbolAsStyle(
                                    cat.symbol(), layer_alpha)}
        style += """
            }
        };"""
    else:
        style = ""
