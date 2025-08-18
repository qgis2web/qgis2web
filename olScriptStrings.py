from . import xmltodict

from qgis2web.olStyleScripts import getStrokeStyle


def measureControlScript():
    measureControl = """let measuring = false;

	const measureButton = document.createElement('button');
	measureButton.className = 'measure-button fas fa-ruler';
	measureButton.title = 'Measure';

	const measureControl = document.createElement('div');
	measureControl.className = 'ol-unselectable ol-control measure-control';
	measureControl.appendChild(measureButton);
	map.getTargetElement().appendChild(measureControl);

	// Event handler
	function handleMeasure() {
	  if (!measuring) {
		selectLabel.style.display = "";
		map.addInteraction(draw);
		createHelpTooltip();
		createMeasureTooltip();
		measuring = true;
	  } else {
		selectLabel.style.display = "none";
		map.removeInteraction(draw);
		map.removeOverlay(helpTooltip);
		map.removeOverlay(measureTooltip);
		const staticTooltips = document.getElementsByClassName("tooltip-static");
		while (staticTooltips.length > 0) {
		  staticTooltips[0].parentNode.removeChild(staticTooltips[0]);
		}
		measureLayer.getSource().clear();
		sketch = null;
		measuring = false;
	  }
	}

	measureButton.addEventListener('click', handleMeasure);
	measureButton.addEventListener('touchstart', handleMeasure);"""
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
    var selectLabel = document.createElement("label");
    selectLabel.innerHTML = "&nbsp;Measure:&nbsp;";

    var typeSelect = document.createElement("select");
    typeSelect.id = "type";

    var measurementOption = [
        { value: "LineString", description: "Length" },
        { value: "Polygon", description: "Area" }
        ];
    measurementOption.forEach(function (option) {
        var optionElement = document.createElement("option");
        optionElement.value = option.value;
        optionElement.text = option.description;
        typeSelect.appendChild(optionElement);
    });

    selectLabel.appendChild(typeSelect);
    measureControl.appendChild(selectLabel);

    selectLabel.style.display = "none";
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



	/**
	 * Message to show when the user is drawing a polygon.
	 * @type {string}
	 */
	var continuePolygonMsg = "1click continue, 2click close";


	var typeSelect = document.getElementById("type");
	var typeSelectForm = document.getElementById("form_measure");

	typeSelect.onchange = function (e) {		  
	  map.removeInteraction(draw);
	  addInteraction();
	  map.addInteraction(draw);		  
	};

	var measureLineStyle = new ol.style.Style({
	  stroke: new ol.style.Stroke({ 
		color: "rgba(0, 0, 255)", //blu
		lineDash: [10, 10],
		width: 4
	  }),
	  image: new ol.style.Circle({
		radius: 6,
		stroke: new ol.style.Stroke({
		  color: "rgba(255, 255, 255)", 
		  width: 1
		}),
	  })
	});

	var measureLineStyle2 = new ol.style.Style({	  
		stroke: new ol.style.Stroke({
			color: "rgba(255, 255, 255)", 
			lineDash: [10, 10],
			width: 2
		  }),
	  image: new ol.style.Circle({
		radius: 5,
		stroke: new ol.style.Stroke({
		  color: "rgba(0, 0, 255)", 
		  width: 1
		}),
			  fill: new ol.style.Fill({
		  color: "rgba(255, 204, 51, 0.4)", 
		}),
		  })
	});

	var labelStyle = new ol.style.Style({
	  text: new ol.style.Text({
		font: "14px Calibri,sans-serif",
		fill: new ol.style.Fill({
		  color: "rgba(0, 0, 0, 1)"
		}),
		stroke: new ol.style.Stroke({
		  color: "rgba(255, 255, 255, 1)",
		  width: 3
		})
	  })
	});

	var labelStyleCache = [];

	var styleFunction = function (feature, type) {
	  var styles = [measureLineStyle, measureLineStyle2];
	  var geometry = feature.getGeometry();
	  var type = geometry.getType();
	  var lineString;
	  if (!type || type === type) {
		if (type === "Polygon") {
		  lineString = new ol.geom.LineString(geometry.getCoordinates()[0]);
		} else if (type === "LineString") {
		  lineString = geometry;
		}
	  }
	  if (lineString) {
		var count = 0;
		lineString.forEachSegment(function (a, b) {
		  var segment = new ol.geom.LineString([a, b]);
		  var label = formatLength(segment);
		  if (labelStyleCache.length - 1 < count) {
			labelStyleCache.push(labelStyle.clone());
		  }
		  labelStyleCache[count].setGeometry(segment);
		  labelStyleCache[count].getText().setText(label);
		  styles.push(labelStyleCache[count]);
		  count++;
		});
	  }
	  return styles;
	};
	var source = new ol.source.Vector();

	var measureLayer = new ol.layer.Vector({
	  source: source,
	  displayInLayerSwitcher: false,
	  style: function (feature) {
		labelStyleCache = [];
		return styleFunction(feature);
	  }
	});

	map.addLayer(measureLayer);

	var draw; // global so we can remove it later
	function addInteraction() {
	  var type = typeSelect.value;
	  draw = new ol.interaction.Draw({
		source: source,
		type: /** @type {ol.geom.GeometryType} */ (type),
		style: function (feature) {
				  return styleFunction(feature, type);
				}
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
			  if (geom instanceof ol.geom.Polygon) {
					  output = formatArea(/** @type {ol.geom.Polygon} */ (geom));
					  tooltipCoord = geom.getInteriorPoint().getCoordinates();
					} else if (geom instanceof ol.geom.LineString) {
					  output = formatLength(/** @type {ol.geom.LineString} */ (geom));
					  tooltipCoord = geom.getLastCoordinate();
					}
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
    measureUnitFeet = """
  function convertToFeet(length) {
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

  /**
  * Format area output.
  * @param {ol.geom.Polygon} polygon The polygon.
  * @return {string} Formatted area.
  */
  var formatArea = function (polygon) {
    var area = polygon.getArea();
    var output;
    if (area > 107639) {  // Converte 1 km^2 in piedi quadrati
      output = (Math.round((area / 107639) * 1000) / 1000) + ' sq mi';
    } else {
      output = (Math.round(area * 10.7639 * 100) / 100) + ' sq ft';
    }
    return output;
  };

  addInteraction();

  var parentElement = document.querySelector(".measure-control");
  var elementToMove = document.getElementById("form_measure");
  if (elementToMove && parentElement) {
    parentElement.insertBefore(elementToMove, parentElement.firstChild);
  }
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

  /**
  * Format area output.
  * @param {ol.geom.Polygon} polygon The polygon.
  * @return {string} Formatted area.
  */
  var formatArea = function (polygon) {
    var area = polygon.getArea();
    var output;
    if (area > 1000000) {
    output =
      Math.round((area / 1000000) * 1000) / 1000 + " " + "km<sup>2</sup>";
    } else {
    output = Math.round(area * 100) / 100 + " " + "m<sup>2</sup>";
    }
    return output;
  };

  addInteraction();

  var parentElement = document.querySelector(".measure-control");
  var elementToMove = document.getElementById("form_measure");
  if (elementToMove && parentElement) {
    parentElement.insertBefore(elementToMove, parentElement.firstChild);
  }
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
  display: flex;
}
.ol-touch .measure-control {
  top: %(touchPos)dpx;
}
.measure-control label {
  padding: 1px;
  padding-right: 4px;
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
  const geolocateOverlay = new ol.layer.Vector({
	  source: new ol.source.Vector({
		features: [accuracyFeature, positionFeature],
	  }),
	});
	
	const geolocation = new ol.Geolocation({
	  projection: map.getView().getProjection(),
	});

	geolocation.on('change:accuracyGeometry', function () {
	  accuracyFeature.setGeometry(geolocation.getAccuracyGeometry());
	});

	geolocation.on('change:position', function () {
	  const coords = geolocation.getPosition();
	  positionFeature.setGeometry(coords ? new ol.geom.Point(coords) : null);
	});

	geolocation.setTracking(true);

	function handleGeolocate() {
	  if (isTracking) {
		map.removeLayer(geolocateOverlay);
		isTracking = false;
	  } else if (geolocation.getTracking()) {
		map.addLayer(geolocateOverlay);
		const pos = geolocation.getPosition();
		if (pos) {
		  map.getView().setCenter(pos);
		}
		isTracking = true;
	  }
	}

	geolocateButton.addEventListener('click', handleGeolocate);
	geolocateButton.addEventListener('touchstart', handleGeolocate);
"""
    else:
        return ""


def geolocationHead(geolocate):
    if geolocate:
        return """
	let isTracking = false;

	const geolocateButton = document.createElement('button');
	geolocateButton.className = 'geolocate-button fa fa-map-marker';
	geolocateButton.title = 'Geolocalizza';

	const geolocateControl = document.createElement('div');
	geolocateControl.className = 'ol-unselectable ol-control geolocate';
	geolocateControl.appendChild(geolocateButton);
	map.getTargetElement().appendChild(geolocateControl);

	const accuracyFeature = new ol.Feature();
	const positionFeature = new ol.Feature({
	  style: new ol.style.Style({
		image: new ol.style.Circle({
		  radius: 6,
		  fill: new ol.style.Fill({ color: '#3399CC' }),
		  stroke: new ol.style.Stroke({ color: '#fff', width: 2 }),
		}),
	  }),
	});"""
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
        <link href="resources/photon-geocoder-autocomplete.min.css" rel="stylesheet">"""
        return returnVal
    else:
        return ""


def geocodeJS(geocode):
    if geocode:
        returnVal = """
        <script src="resources/photon-geocoder-autocomplete.min.js"></script>"""
        return returnVal
    else:
        return ""


def geocodeScript(geocode):
    if geocode != "None":
        return f"""
  //Layer to represent the point of the geocoded address
  var geocoderLayer = new ol.layer.Vector({{
      source: new ol.source.Vector(),
  }});
  map.addLayer(geocoderLayer);
  var vectorSource = geocoderLayer.getSource();

  //Variable used to store the coordinates of geocoded addresses
  var obj2 = {{
  value: '',
  letMeKnow() {{
      //console.log(`Geocoded position: ${{this.gcd}}`);
  }},
  get gcd() {{
      return this.value;
  }},
  set gcd(value) {{
      this.value = value;
      this.letMeKnow();
  }}
  }}

  var obj = {{
      value: '',
      get label() {{
          return this.value;
      }},
      set label(value) {{
          this.value = value;
      }}
  }}

  // Function to handle the selected address
  function onSelected(feature) {{
      obj.label = feature;
      input.value = typeof obj.label.properties.label === "undefined"? obj.label.properties.display_name : obj.label.properties.label;
      var coordinates = ol.proj.transform(
      [feature.geometry.coordinates[0], feature.geometry.coordinates[1]],
      "EPSG:4326",
      map.getView().getProjection()
      );
      vectorSource.clear(true);
      obj2.gcd = [feature.geometry.coordinates[0], feature.geometry.coordinates[1]];
      var marker = new ol.Feature(new ol.geom.Point(coordinates));
      var zIndex = 1;
      marker.setStyle(new ol.style.Style({{
      image: new ol.style.Icon(({{
          anchor: [0.5, 1],
          anchorXUnits: 'fraction',
          anchorYUnits: 'fraction',
          scale: 0.7,
          opacity: 1,
          src: "./resources/marker.png",
          zIndex: zIndex
      }})),
      zIndex: zIndex
      }}));
      vectorSource.addFeature(marker);
      map.getView().setCenter(coordinates);
      map.getView().setZoom(18);
  }}

  // Format the result in the autocomplete search bar
  var formatResult = function (feature, el) {{
      var title = document.createElement("strong");
      el.appendChild(title);
      var detailsContainer = document.createElement("small");
      el.appendChild(detailsContainer);
      var details = [];
      title.innerHTML = feature.properties.label || feature.properties.display_name;
      var types = {{
      housenumber: "numéro",
      street: "rue",
      locality: "lieu-dit",
      municipality: "commune",
      }};
      if (
      feature.properties.city &&
      feature.properties.city !== feature.properties.name
      ) {{
      details.push(feature.properties.city);
      }}
      if (feature.properties.context) {{
      details.push(feature.properties.context);
      }}
      detailsContainer.innerHTML = details.join(", ");
  }};

  // Define a class to create the control button for the search bar in a div tag
  class AddDomControl extends ol.control.Control {{
      constructor(elementToAdd, opt_options) {{
      const options = opt_options || {{}};

      const element = document.createElement("div");
      if (options.className) {{
          element.className = options.className;
      }}
      element.appendChild(elementToAdd);

      super({{
          element: element,
          target: options.target,
      }});
      }}
  }}

  // Function to show you can do something with the returned elements
  function myHandler(featureCollection) {{
      //console.log(featureCollection);
  }}

  // URL for API
  const url = {{"Nominatim OSM": "https://nominatim.openstreetmap.org/search?format=geojson&addressdetails=1&",
  "France BAN": "https://api-adresse.data.gouv.fr/search/?"}}
  var API_URL = "//api-adresse.data.gouv.fr";

  // Create search by adresses component
  var containers = new Photon.Search({{
    resultsHandler: myHandler,
    onSelected: onSelected,
    placeholder: "Search an address",
    formatResult: formatResult,
    //url: API_URL + "/search/?",
    url: url["{geocode}"],
    position: "topright",
    // ,includePosition: function() {{
    //   return ol.proj.transform(
    //     map.getView().getCenter(),
    //     map.getView().getProjection(), //'EPSG:3857',
    //     'EPSG:4326'
    //   );
    // }}
  }});

  // Add the created DOM element within the map
  //var left = document.getElementById("top-left-container");
  var controlGeocoder = new AddDomControl(containers, {{
    className: "photon-geocoder-autocomplete ol-unselectable ol-control",
  }});
  map.addControl(controlGeocoder);
  var search = document.getElementsByClassName("photon-geocoder-autocomplete ol-unselectable ol-control")[0];
  search.style.display = "flex";

  // Create the new button element
  var button = document.createElement("button");
  button.type = "button";
  button.id = "gcd-button-control";
  button.className = "gcd-gl-btn fa fa-search leaflet-control";

  // Ajouter le bouton à l'élément parent
  search.insertBefore(button, search.firstChild);
  last = search.lastChild;
  last.style.display = "none";
  button.addEventListener("click", function (e) {{
      if (last.style.display === "none") {{
          last.style.display = "block";
      }} else {{
          last.style.display = "none";
      }}
  }});
  input = document.getElementsByClassName("photon-input")[0];
  //var searchbar = document.getElementsByClassName("photon-geocoder-autocomplete ol-unselectable ol-control")[0]
  //left.appendChild(searchbar);
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



