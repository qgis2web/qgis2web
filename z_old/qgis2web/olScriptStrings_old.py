from . import xmltodict

from qgis2web.olStyleScripts import getStrokeStyle


def measureControlScript():
    measureControl = """
var measuring = false;
var measureControl = (function (Control) {
    measureControl = function(opt_options) {

      var options = opt_options || {};

      var button = document.createElement('button');
      button.className += ' fas fa-ruler ';

      var this_ = this;
      var handleMeasure = function(e) {
        if (!measuring) {
            this_.getMap().addInteraction(draw);
            createHelpTooltip();
            createMeasureTooltip();
            measuring = true;
        } else {
            this_.getMap().removeInteraction(draw);
            measuring = false;
            this_.getMap().removeOverlay(helpTooltip);
            this_.getMap().removeOverlay(measureTooltip);
        }
      };

      button.addEventListener('click', handleMeasure, false);
      button.addEventListener('touchstart', handleMeasure, false);

      var element = document.createElement('div');
      element.className = 'measure-control ol-unselectable ol-control';
      element.appendChild(button);

      ol.control.Control.call(this, {
        element: element,
        target: options.target
      });

    };
    if (Control) measureControl.__proto__ = Control;
    measureControl.prototype = Object.create(Control && Control.prototype);
    measureControl.prototype.constructor = measureControl;
    return measureControl;
}(ol.control.Control));"""
    return measureControl


def measuringScript():
    measuring = """
    map.on('pointermove', function(evt) {
        if (evt.dragging) {
            return;
        }
        if (measuring) {
            /** @type {string} */
            var helpMsg = 'Click to start drawing';
            if (sketch) {
                var geom = (sketch.getGeometry());
                if (geom instanceof ol.geom.Polygon) {
                    helpMsg = continuePolygonMsg;
                } else if (geom instanceof ol.geom.LineString) {
                    helpMsg = continueLineMsg;
                }
            }
            helpTooltipElement.innerHTML = helpMsg;
            helpTooltip.setPosition(evt.coordinate);
        }
    });
    """
    return measuring


def measureScript():
    measure = """
/**
 * Currently drawn feature.
 * @type {ol.Feature}
 */

/**
 * The help tooltip element.
 * @type {Element}
 */
var helpTooltipElement;


/**
 * Overlay to show the help messages.
 * @type {ol.Overlay}
 */
var helpTooltip;


/**
 * The measure tooltip element.
 * @type {Element}
 */
var measureTooltipElement;


/**
 * Overlay to show the measurement.
 * @type {ol.Overlay}
 */
var measureTooltip;


/**
 * Message to show when the user is drawing a line.
 * @type {string}
 */
var continueLineMsg = 'Click to continue drawing the line';






var source = new ol.source.Vector();

var measureLayer = new ol.layer.Vector({
    source: source,
    style: new ol.style.Style({
        fill: new ol.style.Fill({
            color: 'rgba(255, 255, 255, 0.2)'
        }),
        stroke: new ol.style.Stroke({
            color: '#ffcc33',
            width: 3
        }),
        image: new ol.style.Circle({
            radius: 7,
            fill: new ol.style.Fill({
                color: '#ffcc33'
            })
        })
    })
});

map.addLayer(measureLayer);

var draw; // global so we can remove it later
function addInteraction() {
  var type = 'LineString';
  draw = new ol.interaction.Draw({
    source: source,
    type: /** @type {ol.geom.GeometryType} */ (type),
    style: new ol.style.Style({
      fill: new ol.style.Fill({
        color: 'rgba(255, 255, 255, 0.2)'
      }),
      stroke: new ol.style.Stroke({
        color: 'rgba(0, 0, 0, 0.5)',
        lineDash: [10, 10],
        width: 2
      }),
      image: new ol.style.Circle({
        radius: 5,
        stroke: new ol.style.Stroke({
          color: 'rgba(0, 0, 0, 0.7)'
        }),
        fill: new ol.style.Fill({
          color: 'rgba(255, 255, 255, 0.2)'
        })
      })
    })
  });

  var listener;
  draw.on('drawstart',
      function(evt) {
        // set sketch
        sketch = evt.feature;

        /** @type {ol.Coordinate|undefined} */
        var tooltipCoord = evt.coordinate;

        listener = sketch.getGeometry().on('change', function(evt) {
          var geom = evt.target;
          var output;
            output = formatLength( /** @type {ol.geom.LineString} */ (geom));
            tooltipCoord = geom.getLastCoordinate();
          measureTooltipElement.innerHTML = output;
          measureTooltip.setPosition(tooltipCoord);
        });
      }, this);

  draw.on('drawend',
      function(evt) {
        measureTooltipElement.className = 'tooltip tooltip-static';
        measureTooltip.setOffset([0, -7]);
        // unset sketch
        sketch = null;
        // unset tooltip so that a new one can be created
        measureTooltipElement = null;
        createMeasureTooltip();
        ol.Observable.unByKey(listener);
      }, this);
}


/**
 * Creates a new help tooltip
 */
function createHelpTooltip() {
  if (helpTooltipElement) {
    helpTooltipElement.parentNode.removeChild(helpTooltipElement);
  }
  helpTooltipElement = document.createElement('div');
  helpTooltipElement.className = 'tooltip hidden';
  helpTooltip = new ol.Overlay({
    element: helpTooltipElement,
    offset: [15, 0],
    positioning: 'center-left'
  });
  map.addOverlay(helpTooltip);
}


/**
 * Creates a new measure tooltip
 */
function createMeasureTooltip() {
  if (measureTooltipElement) {
    measureTooltipElement.parentNode.removeChild(measureTooltipElement);
  }
  measureTooltipElement = document.createElement('div');
  measureTooltipElement.className = 'tooltip tooltip-measure';
  measureTooltip = new ol.Overlay({
    element: measureTooltipElement,
    offset: [0, -15],
    positioning: 'bottom-center'
  });
  map.addOverlay(measureTooltip);
}

"""
    return measure


def measureUnitFeetScript():
    measureUnitFeet = """function convertToFeet(length) {
    feet_length = length * 3.2808;
    return feet_length
}

/**
 * format length output
 * @param {ol.geom.LineString} line
 * @return {string}
 */
var formatLength = function(line) {
  var length;
  var coordinates = line.getCoordinates();
  length = 0;
  var sourceProj = map.getView().getProjection();
  for (var i = 0, ii = coordinates.length - 1; i < ii; ++i) {
      var c1 = ol.proj.transform(coordinates[i], sourceProj, 'EPSG:4326');
      var c2 = ol.proj.transform(coordinates[i + 1], sourceProj, 'EPSG:4326');
      length += ol.sphere.getDistance(c1, c2);
    }
    feet_length = convertToFeet(length)

    var output;
    if (feet_length > 5280) {
        output = (Math.round(feet_length / 5280 * 100) / 100) + ' miles';
    } else {
        output = (Math.round(feet_length * 100) / 100) + ' ft';
    }
    return output;
};

addInteraction();
"""
    return measureUnitFeet


def measureUnitMetricScript():
    measureUnitMetric = """
/**
 * format length output
 * @param {ol.geom.LineString} line
 * @return {string}
 */
var formatLength = function(line) {
  var length;
  var coordinates = line.getCoordinates();
  length = 0;
  var sourceProj = map.getView().getProjection();
  for (var i = 0, ii = coordinates.length - 1; i < ii; ++i) {
      var c1 = ol.proj.transform(coordinates[i], sourceProj, 'EPSG:4326');
      var c2 = ol.proj.transform(coordinates[i + 1], sourceProj, 'EPSG:4326');
      length += ol.sphere.getDistance(c1, c2);
    }
  var output;
  if (length > 100) {
    output = (Math.round(length / 1000 * 100) / 100) +
        ' ' + 'km';
  } else {
    output = (Math.round(length * 100) / 100) +
        ' ' + 'm';
  }
  return output;
};

addInteraction();
"""
    return measureUnitMetric


def measureStyleScript(controlCount):
    pos = 65 + (controlCount * 35)
    touchPos = 80 + (controlCount * 50)
    measureStyle = """
<style>
.tooltip {
  position: relative;
  background: rgba(0, 0, 0, 0.5);
  border-radius: 4px;
  color: white;
  padding: 4px 8px;
  opacity: 0.7;
  white-space: nowrap;
}
.tooltip-measure {
  opacity: 1;
  font-weight: bold;
}
.tooltip-static {
  background-color: #ffcc33;
  color: black;
  border: 1px solid white;
}
.tooltip-measure:before,
.tooltip-static:before {
  border-top: 6px solid rgba(0, 0, 0, 0.5);
  border-right: 6px solid transparent;
  border-left: 6px solid transparent;
  content: "";
  position: absolute;
  bottom: -6px;
  margin-left: -7px;
  left: 50%%;
}
.tooltip-static:before {
  border-top-color: #ffcc33;
}
.measure-control {
  top: %(pos)dpx;
  left: .5em;
}
.ol-touch .measure-control {
  top: %(touchPos)dpx;
}
</style>""" % {"pos": pos, "touchPos": touchPos}
    return measureStyle


def layerSearchStyleScript(controlCount):
    pos = 65 + (controlCount * 35)
    touchPos = 80 + (controlCount * 50)
    layerSearchStyle = """
<style>
.search-layer {
  top: %(pos)dpx;
  left: .5em;
}
.ol-touch .search-layer {
  top: %(touchPos)dpx;
}
</style>""" % {"pos": pos, "touchPos": touchPos}
    return (layerSearchStyle, controlCount)


def geolocation(geolocate):
    if geolocate:
        return """
      var geolocation = new ol.Geolocation({
  projection: map.getView().getProjection()
});


var accuracyFeature = new ol.Feature();
geolocation.on('change:accuracyGeometry', function() {
  accuracyFeature.setGeometry(geolocation.getAccuracyGeometry());
});

var positionFeature = new ol.Feature();
positionFeature.setStyle(new ol.style.Style({
  image: new ol.style.Circle({
    radius: 6,
    fill: new ol.style.Fill({
      color: '#3399CC'
    }),
    stroke: new ol.style.Stroke({
      color: '#fff',
      width: 2
    })
  })
}));

geolocation.on('change:position', function() {
  var coordinates = geolocation.getPosition();
  positionFeature.setGeometry(coordinates ?
      new ol.geom.Point(coordinates) : null);
});

var geolocateOverlay = new ol.layer.Vector({
  source: new ol.source.Vector({
    features: [accuracyFeature, positionFeature]
  })
});

geolocation.setTracking(true);
"""
    else:
        return ""


def geolocationHead(geolocate):
    if geolocate:
        return """
isTracking = false;
var geolocateControl = (function (Control) {
    geolocateControl = function(opt_options) {
        var options = opt_options || {};
        var button = document.createElement('button');
        button.className += ' fa fa-map-marker';
        var handleGeolocate = function() {
            if (isTracking) {
                map.removeLayer(geolocateOverlay);
                isTracking = false;
          } else if (geolocation.getTracking()) {
                map.addLayer(geolocateOverlay);
                map.getView().setCenter(geolocation.getPosition());
                isTracking = true;
          }
        };
        button.addEventListener('click', handleGeolocate, false);
        button.addEventListener('touchstart', handleGeolocate, false);
        var element = document.createElement('div');
        element.className = 'geolocate ol-unselectable ol-control';
        element.appendChild(button);
        ol.control.Control.call(this, {
            element: element,
            target: options.target
        });
    };
    if (Control) geolocateControl.__proto__ = Control;
    geolocateControl.prototype = Object.create(Control && Control.prototype);
    geolocateControl.prototype.constructor = geolocateControl;
    return geolocateControl;
}(ol.control.Control));"""
    else:
        return ""


def geolocateStyle(geolocate, controlCount):
    if geolocate:
        ctrlPos = 65 + (controlCount * 35)
        touchCtrlPos = 80 + (controlCount * 50)
        controlCount = controlCount + 1
        return ("""
        <style>
        .geolocate {
            top: %dpx;
            left: .5em;
        }
        .ol-touch .geolocate {
            top: %dpx;
        }
        </style>""" % (ctrlPos, touchCtrlPos), controlCount)
    else:
        return ("", controlCount)


def geocodeLinks(geocode):
    if geocode:
        returnVal = """
        <link href="resources/ol-geocoder.min.css" rel="stylesheet">"""
        return returnVal
    else:
        return ""


def geocodeJS(geocode):
    if geocode:
        returnVal = """
        <script src="resources/ol-geocoder.js"></script>"""
        return returnVal
    else:
        return ""


def geocodeScript(geocode):
    if geocode:
        return """
var geocoder = new Geocoder('nominatim', {
  provider: 'osm',
  lang: 'en-US',
  placeholder: 'Search for ...',
  limit: 5,
  keepOpen: true
});
map.addControl(geocoder);

document.getElementsByClassName('gcd-gl-btn')[0].className += ' fa fa-search';
"""
    else:
        return ""


def getGrid(project):
    grid = ""
    if project.readBoolEntry("Grid", "/Enabled", False)[0]:
        stroke = project.readEntry("Grid", "/LineSymbol", "")[0]
        strokeDict = xmltodict.parse(stroke)
        symbol = strokeDict["symbol"]
        layer = symbol["layer"]
        props = layer["prop"]
        lineunits = "px"
        linecap = 0
        linejoin = 0
        width = 1
        color = "#000000"
        dashed = "no"
        for prop in props:
            if prop["@k"] == "line_color":
                color = "'rgba(%s)'" % prop["@v"]
            if prop["@k"] == "line_style":
                dashed = prop["@v"]
            if prop["@k"] == "line_width":
                width = prop["@v"]
            if prop["@k"] == "capstyle":
                linecap = prop["@v"]
            if prop["@k"] == "joinstyle":
                linejoin = prop["@v"]
        strokeStyle, _ = getStrokeStyle(color, dashed, width, lineunits,
                                        linecap, linejoin)
        strokeStyle = strokeStyle.replace("stroke:", "strokeStyle:")
        grid = """
    var gcl = new ol.Graticule({%s});
    gcl.setMap(map);""" % strokeStyle
    return grid


def getM2px(mapUnitsLayers):
    m2px = ""
    if len(mapUnitsLayers) > 0:
        m2px = """
function m2px(m) {
    var centerLatLng = map.getView().getCenter();
    var pointC = map.getPixelFromCoordinate(centerLatLng);
    var pointX = [pointC[0] + 100, pointC[1]];
    var latLngC = map.getCoordinateFromPixel(pointC);
    var latLngX = map.getCoordinateFromPixel(pointX);
    var lineX = new ol.geom.LineString([latLngC, latLngX]);
    var distanceX = lineX.getLength() / 100;
    reciprocal = 1 / distanceX;
    px = Math.ceil(reciprocal);
    return px;
}"""
    return m2px


def getMapUnitLayers(mapUnitsLayers):
    mapUnitLayers = ""
    if len(mapUnitsLayers) > 0:
        lyrs = []
        for layer in mapUnitsLayers:
            lyrs.append("""
            lyr_%s.setStyle(style_%s);""" % (layer, layer))
        lyrScripts = "".join(lyrs)
        mapUnitLayers = """
map.getView().on('change:resolution', function(evt){
%s
});""" % lyrScripts
    return mapUnitLayers
