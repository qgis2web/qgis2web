from . import togeostyler
from . import fromgeostyler

import os
import zipfile
import json
from shutil import copyfile
from bridgestyle import qgis
from bridgestyle import sld
from bridgestyle import mapboxgl
from bridgestyle import mapserver
from qgis.core import (
    QgsWkbTypes,
    QgsMarkerSymbol,
    QgsSymbol,
    QgsSVGFillSymbolLayer,
    QgsSvgMarkerSymbolLayer,
    QgsRasterLayer,
    QgsVectorLayer,
)
from qgis.PyQt.QtCore import QSize, Qt
from qgis.PyQt.QtGui import QColor, QImage, QPainter


def layerStyleAsSld(layer):
    geostyler, icons, warnings = togeostyler.convert(layer)
    sldString, sldWarnings = sld.fromgeostyler.convert(geostyler)
    warnings.extend(sldWarnings)
    return sldString, icons, warnings


def saveLayerStyleAsSld(layer, filename):
    sldstring, icons, warnings = layerStyleAsSld(layer)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(sldstring)
    return warnings


def saveLayerStyleAsZippedSld(layer, filename):
    sldstring, icons, warnings = layerStyleAsSld(layer)
    z = zipfile.ZipFile(filename, "w")
    for icon in icons.keys():
        if icon:
            z.write(icon, os.path.basename(icon))
    z.writestr(layer.name() + ".sld", sldstring)
    z.close()
    return warnings

def layerStyleAsMapbox(layer):
    geostyler, icons, warnings = togeostyler.convert(layer)
    mbox, mbWarnings = mapboxgl.fromgeostyler.convert(geostyler)
    warnings.extend(mbWarnings)
    return mbox, icons, warnings

def layerStylesAsMapboxFolder(layers, folder):
    geostylers = []
    allWarnings = []
    allIcons = {}
    for layer in layers:
        geostyler, icons, warnings = togeostyler.convert(layer)
        geostylers.append(geostyler)
        allWarnings.extend(warnings)
        allIcons.update(icons)
    mbox, mbWarnings = mapboxgl.fromgeostyler.convert(geostylers)
    filename = os.path.join(folder, "style.mapbox")
    print(filename)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(mbox)
    saveSpritesSheet(allIcons, folder)
    allWarnings.extend(mbWarnings)
    return allWarnings

def layerStyleAsMapfile(layer):
    geostyler, icons, warnings = togeostyler.convert(layer)
    mserver, mserverSymbols, msWarnings = mapserver.fromgeostyler.convert(geostyler)
    warnings.extend(msWarnings)
    return mserver, mserverSymbols, icons, warnings


def layerStyleAsMapfileFolder(layer, folder, additional=None):
    geostyler, icons, warnings = togeostyler.convert(layer)
    mserverDict, mserverSymbolsDict, msWarnings = mapserver.fromgeostyler.convertToDict(
        geostyler
    )
    warnings.extend(msWarnings)
    additional = additional or {}
    mserverDict["LAYER"].update(additional)
    mapfile = mapserver.fromgeostyler.convertDictToMapfile(mserverDict)
    symbols = mapserver.fromgeostyler.convertDictToMapfile(
        {"SYMBOLS": mserverSymbolsDict}
    )
    filename = os.path.join(folder, layer.name() + ".txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(mapfile)
    filename = os.path.join(folder, layer.name() + "_symbols.txt")
    with open(filename, "w", encoding="utf-8") as f:
        f.write(symbols)
    for icon in icons:
        dst = os.path.join(folder, os.path.basename(icon))
        copyfile(icon, dst)
    return warnings


NO_ICON = "no_icon"


def saveSymbolLayerSprite(symbolLayer):
    sl = symbolLayer.clone()
    if isinstance(sl, QgsSVGFillSymbolLayer):
        patternWidth = sl.patternWidth()
        color = sl.svgFillColor()
        outlineColor = sl.svgOutlineColor()
        sl = QgsSvgMarkerSymbolLayer(sl.svgFilePath())
        sl.setFillColor(color)
        sl.setOutlineColor(outlineColor)
        sl.setSize(patternWidth)
        sl.setOutputUnit(QgsSymbol.Pixel)
    sl2x = sl.clone()
    try:
        sl2x.setSize(sl2x.size() * 2)
    except AttributeError:
        return None, None
    newSymbol = QgsMarkerSymbol()
    newSymbol.appendSymbolLayer(sl)
    newSymbol.deleteSymbolLayer(0)
    newSymbol2x = QgsMarkerSymbol()
    newSymbol2x.appendSymbolLayer(sl2x)
    newSymbol2x.deleteSymbolLayer(0)
    img = newSymbol.asImage(QSize(sl.size(), sl.size()))
    img2x = newSymbol2x.asImage(QSize(sl2x.size(), sl2x.size()))
    return img, img2x


def saveSpritesSheet(icons, folder):
    sprites = {}
    for iconPath, sl in icons.items():
        iconName = os.path.splitext(os.path.basename(iconPath))[0]
        sprites[iconName] = saveSymbolLayerSprite(sl)
    if sprites:
        height = max([s.height() for s, s2x in sprites.values()])
        width = sum([s.width() for s, s2x in sprites.values()])
        img = QImage(width, height, QImage.Format_ARGB32)
        img.fill(QColor(Qt.transparent))
        img2x = QImage(width * 2, height * 2, QImage.Format_ARGB32)
        img2x.fill(QColor(Qt.transparent))
        painter = QPainter(img)
        painter.begin(img)
        painter2x = QPainter(img2x)
        painter2x.begin(img2x)
        spritesheet = {
            NO_ICON: {"width": 0, "height": 0, "x": 0, "y": 0, "pixelRatio": 1}
        }
        spritesheet2x = {
            NO_ICON: {"width": 0, "height": 0, "x": 0, "y": 0, "pixelRatio": 1}
        }
        x = 0
        for name, _sprites in sprites.items():
            s, s2x = _sprites
            painter.drawImage(x, 0, s)
            painter2x.drawImage(x * 2, 0, s2x)
            spritesheet[name] = {
                "width": s.width(),
                "height": s.height(),
                "x": x,
                "y": 0,
                "pixelRatio": 1,
            }
            spritesheet2x[name] = {
                "width": s2x.width(),
                "height": s2x.height(),
                "x": x * 2,
                "y": 0,
                "pixelRatio": 2,
            }
            x += s.width()
        painter.end()
        painter2x.end()
        img.save(os.path.join(folder, "spriteSheet.png"))
        img2x.save(os.path.join(folder, "spriteSheet@2x.png"))
        with open(os.path.join(folder, "spriteSheet.json"), "w") as f:
            json.dump(spritesheet, f)
        with open(os.path.join(folder, "spriteSheet@2x.json"), "w") as f:
            json.dump(spritesheet2x, f)
