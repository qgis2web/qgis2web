import sys
import os
import shutil
sys.path.append(os.path.dirname(__file__))
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
                       QgsSvgMarkerSymbolLayer)  # noqa
from qgis2web.exp2js import compile_to_file  # noqa
from qgis2web.utils import getRGBAColor, handleHiddenField  # noqa
import bridgestyle  # noqa
import json  # noqa

COLOR = 1
NUMERIC = 2

defaultPropVal = {
    "circle-opacity": 0,
    "circle-radius": 0,
    "circle-stroke-width": 0,
    "circle-stroke-color": "#000000",
    "circle-color": "#ffffff",
    "line-opacity": 0,
    "line-width": 0,
    "line-dasharray": "[10,5]",
    "line-color": "#ffffff",
    "fill-opacity": 0,
    "fill-color": "#ffffff",
    "text-color": "#000000",
    "icon-image": "none",
    "icon-rotate": "0"
}


def getLayerStyle(layer):
    mapboxStyle = bridgestyle.qgis.layerStyleAsMapbox(layer)
    styleJSON = mapboxStyle[0]
    style = json.loads(styleJSON)
    layoutProps = {}
    paintProps = {}

    for eachLayer in style["layers"]:
        layer = eachLayer
        if "filter" in layer:
            if "layout" in layer:
                for prop in layer["layout"]:
                    if layer["filter"] != "ELSE":
                        if prop in layoutProps:
                            layoutProps[prop].extend([layer["filter"],
                                                      layer["layout"][prop]])
                        else:
                            if layer["filter"] != "ELSE":
                                layoutProps[prop] = ["case",
                                                     layer["filter"],
                                                     layer["layout"][prop]]
                    else:
                        layoutProps[prop].append(layer["layout"][prop])
            if "paint" in layer:
                for prop in layer["paint"]:
                    if layer["filter"] != "ELSE":
                        if prop in paintProps:
                            paintProps[prop].extend([layer["filter"],
                                                    layer["paint"][prop]])
                        else:
                            if layer["filter"] != "ELSE":
                                paintProps[prop] = ["case",
                                                    layer["filter"],
                                                    layer["paint"][prop]]
                    else:
                        paintProps[prop].append(layer["paint"][prop])
            layer.pop("filter")
        else:
            if len(layoutProps) > 0:
                for prop in layer["layout"]:
                    layerProps[prop].append(layer["layout"][prop])
            if len(paintProps) > 0:
                for prop in layer["paint"]:
                    if prop[:4] != "text":
                        try:
                            paintProps[prop].append(layer["paint"][prop])
                        except:
                            paintProps[prop] = [layer["paint"][prop]]

    if len(layoutProps) > 0:
        style["layers"][0][0]["layout"] = layoutProps
        for prop in layoutProps:
            if len(layoutProps[prop]) % 2 == 1:
                layoutProps[prop].append(defaultPropVal[prop])
    if len(paintProps) > 0:
        style["layers"][0]["paint"] = paintProps
        for prop in paintProps:
            if len(paintProps[prop]) % 2 == 1:
                if prop[:4] != "text":
                    try:
                        paintProps[prop].append(defaultPropVal[prop])
                    except:
                        paintProps[prop] = [defaultPropVal[prop]]
    return style["layers"]
