def writeHTMLstart(settings, controlCount, osmb):
    jsAddress = '<script src="resources/polyfills.js"></script>'
    if settings["Data export"]["Mapping library location"] == "Local":
        cssAddress = """<link rel="stylesheet" """
        cssAddress += """href="./resources/ol.css" />"""
        jsAddress += """
        <script src="./resources/ol.js"></script>"""
    else:
        cssAddress = """<link rel="stylesheet" href="http://"""
        cssAddress += "cdnjs.cloudflare.com/ajax/libs/openlayers/"
        cssAddress += """4.0.1/ol.css" />"""
        jsAddress += """
        <script src="https://cdnjs.cloudflare.com/ajax/libs/openlayers/"""
        jsAddress += """4.0.1/ol.js"></script>"""
    layerSearch = unicode(settings["Appearance"]["Layer search"])
    if layerSearch != "None" and layerSearch != "":
        searchLayer = settings["Appearance"]["Search layer"]
        cssAddress += """
        <link rel="stylesheet" href="resources/horsey.min.css">
        <link rel="stylesheet" href="resources/ol3-search-layer.min.css">"""
        jsAddress += """
        <script src="http://cdn.polyfill.io/v2/polyfill.min.js?features="""
        jsAddress += """Element.prototype.classList,URL"></script>
        <script src="resources/horsey.min.js"></script>
        <script src="resources/ol3-search-layer.min.js"></script>"""
        searchVals = layerSearch.split(": ")
        layerSearch = u"""
    var searchLayer = new ol.SearchLayer({{
      layer: lyr_{layer},
      colName: '{field}',
      zoom: 10,
      collapsed: true,
      map: map
    }});

    map.addControl(searchLayer);""".format(layer=searchLayer,
                                           field=searchVals[1])
        controlCount = controlCount + 1
    else:
        layerSearch = ""
    if osmb != "":
        jsAddress += """
        <script src="resources/OSMBuildings-OL3.js"></script>"""
    return (jsAddress, cssAddress, layerSearch, controlCount)