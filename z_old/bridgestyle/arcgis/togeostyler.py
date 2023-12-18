import os
import json

_usedIcons = {}
_warnings = []

def convert(layer):
    global _usedIcons
    _usedIcons = {}
    global _warnings
    _warnings = []
    geostyler = processLayer(layer)
    return geostyler, _usedIcons, _warnings

def processLayer(layer):
    #layer is a dictionary with the ArcGIS Pro Json style    
    #return geostyler
    pass