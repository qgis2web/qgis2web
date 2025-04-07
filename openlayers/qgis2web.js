
var map = new ol.Map({
    target: 'map',
    renderer: 'canvas',
    layers: layersList,
    view: new ol.View({
        @VIEW@
    })
});

//initial view - epsg:3857 coordinates if not "Match project CRS"
map.getView().fit(@BOUNDS@, map.getSize());

////small screen definition
    var hasTouchScreen = map.getViewport().classList.contains('ol-touch');
    var isSmallScreen = window.innerWidth < 650;

////controls container

    //top left container
    var topLeftContainer = new ol.control.Control({
        element: (() => {
            var topLeftContainer = document.createElement('div');
            topLeftContainer.id = 'top-left-container';
            return topLeftContainer;
        })(),
    });
    map.addControl(topLeftContainer)

    //bottom left container
    var bottomLeftContainer = new ol.control.Control({
        element: (() => {
            var bottomLeftContainer = document.createElement('div');
            bottomLeftContainer.id = 'bottom-left-container';
            return bottomLeftContainer;
        })(),
    });
    map.addControl(bottomLeftContainer)
  
    //top right container
    var topRightContainer = new ol.control.Control({
        element: (() => {
            var topRightContainer = document.createElement('div');
            topRightContainer.id = 'top-right-container';
            return topRightContainer;
        })(),
    });
    map.addControl(topRightContainer)

    //bottom right container
    var bottomRightContainer = new ol.control.Control({
        element: (() => {
            var bottomRightContainer = document.createElement('div');
            bottomRightContainer.id = 'bottom-right-container';
            return bottomRightContainer;
        })(),
    });
    map.addControl(bottomRightContainer)

//popup
var container = document.getElementById('popup');
var content = document.getElementById('popup-content');
var closer = document.getElementById('popup-closer');
var sketch;

closer.onclick = function() {
    container.style.display = 'none';
    closer.blur();
    return false;
};
var overlayPopup = new ol.Overlay({
    element: container,
	autoPan: true
});
map.addOverlay(overlayPopup)
    
    
var NO_POPUP = 0
var ALL_FIELDS = 1

/**
 * Returns either NO_POPUP, ALL_FIELDS or the name of a single field to use for
 * a given layer
 * @param layerList {Array} List of ol.Layer instances
 * @param layer {ol.Layer} Layer to find field info about
 */
function getPopupFields(layerList, layer) {
    // Determine the index that the layer will have in the popupLayers Array,
    // if the layersList contains more items than popupLayers then we need to
    // adjust the index to take into account the base maps group
    var idx = layersList.indexOf(layer) - (layersList.length - popupLayers.length);
    return popupLayers[idx];
}

//highligth collection
var collection = new ol.Collection();
var featureOverlay = new ol.layer.Vector({
    map: map,
    source: new ol.source.Vector({
        features: collection,
        useSpatialIndex: false // optional, might improve performance
    }),
    style: [new ol.style.Style({
        stroke: new ol.style.Stroke({
            color: '#f00',
            width: 1
        }),
        fill: new ol.style.Fill({
            color: 'rgba(255,0,0,0.1)'
        }),
    })],
    updateWhileAnimating: true, // optional, for instant visual feedback
    updateWhileInteracting: true // optional, for instant visual feedback
});

var doHighlight = @DOHIGHLIGHT@;
var doHover = @ONHOVER@;

function createPopupField(currentFeature, currentFeatureKeys, layer) {
    var popupText = '';
    for (var i = 0; i < currentFeatureKeys.length; i++) {
        if (currentFeatureKeys[i] != 'geometry' && currentFeatureKeys[i] != 'layerObject' && currentFeatureKeys[i] != 'idO') {
            var popupField = '';
            if (layer.get('fieldLabels')[currentFeatureKeys[i]] == "hidden field") {
                continue;
            } else if (layer.get('fieldLabels')[currentFeatureKeys[i]] == "inline label - visible with data") {
                if (currentFeature.get(currentFeatureKeys[i]) == null) {
                    continue;
                }
            }
            if (layer.get('fieldLabels')[currentFeatureKeys[i]] == "inline label - always visible" ||
                layer.get('fieldLabels')[currentFeatureKeys[i]] == "inline label - visible with data") {
                popupField += '<th>' + layer.get('fieldAliases')[currentFeatureKeys[i]] + '</th><td>';
            } else {
                popupField += '<td colspan="2">';
            }
            if (layer.get('fieldLabels')[currentFeatureKeys[i]] == "header label - visible with data") {
                if (currentFeature.get(currentFeatureKeys[i]) == null) {
                    continue;
                }
            }
            if (layer.get('fieldLabels')[currentFeatureKeys[i]] == "header label - always visible" ||
                layer.get('fieldLabels')[currentFeatureKeys[i]] == "header label - visible with data") {
                popupField += '<strong>' + layer.get('fieldAliases')[currentFeatureKeys[i]] + '</strong><br />';
            }
            if (layer.get('fieldImages')[currentFeatureKeys[i]] != "ExternalResource") {
				popupField += (currentFeature.get(currentFeatureKeys[i]) != null ? autolinker.link(currentFeature.get(currentFeatureKeys[i]).toLocaleString()) + '</td>' : '');
			} else {
				var fieldValue = currentFeature.get(currentFeatureKeys[i]);
				if (/\.(gif|jpg|jpeg|tif|tiff|png|avif|webp|svg)$/i.test(fieldValue)) {
					popupField += (fieldValue != null ? '<img src="images/' + fieldValue.replace(/[\\\/:]/g, '_').trim() + '" /></td>' : '');
				} else if (/\.(mp4|webm|ogg|avi|mov|flv)$/i.test(fieldValue)) {
					popupField += (fieldValue != null ? '<video controls><source src="images/' + fieldValue.replace(/[\\\/:]/g, '_').trim() + '" type="video/mp4">Il tuo browser non supporta il tag video.</video></td>' : '');
				} else {
					popupField += (fieldValue != null ? autolinker.link(fieldValue.toLocaleString()) + '</td>' : '');
				}
			}
            popupText += '<tr>' + popupField + '</tr>';
        }
    }
    return popupText;
}

var highlight;
var autolinker = new Autolinker({truncate: {length: 30, location: 'smart'}});

function onPointerMove(evt) {
    if (!doHover && !doHighlight) {
        return;
    }
    var pixel = map.getEventPixel(evt.originalEvent);
    var coord = evt.coordinate;
    var currentFeature;
    var currentLayer;
    var currentFeatureKeys;
    var clusteredFeatures;
    var clusterLength;
    var popupText = '<ul>';
    map.forEachFeatureAtPixel(pixel, function(feature, layer) {
        if (layer && feature instanceof ol.Feature && (layer.get("interactive") || layer.get("interactive") == undefined)) {
            var doPopup = false;
            for (k in layer.get('fieldImages')) {
                if (layer.get('fieldImages')[k] != "Hidden") {
                    doPopup = true;
                }
            }
            currentFeature = feature;
            currentLayer = layer;
            clusteredFeatures = feature.get("features");
            if (clusteredFeatures) {
				clusterLength = clusteredFeatures.length;
			}
            if (typeof clusteredFeatures !== "undefined") {
                if (doPopup) {
                    for(var n=0; n<clusteredFeatures.length; n++) {
                        currentFeature = clusteredFeatures[n];
                        currentFeatureKeys = currentFeature.getKeys();
                        popupText += '<li><table>'
                        popupText += '<a>' + '<b>' + layer.get('popuplayertitle') + '</b>' + '</a>';
                        popupText += createPopupField(currentFeature, currentFeatureKeys, layer);
                        popupText += '</table></li>';    
                    }
                }
            } else {
                currentFeatureKeys = currentFeature.getKeys();
                if (doPopup) {
                    popupText += '<li><table>';
                    popupText += '<a>' + '<b>' + layer.get('popuplayertitle') + '</b>' + '</a>';
                    popupText += createPopupField(currentFeature, currentFeatureKeys, layer);
                    popupText += '</table></li>';
                }
            }
        }
    });
    if (popupText == '<ul>') {
        popupText = '';
    } else {
        popupText += '</ul>';
    }
    
	if (doHighlight) {
        if (currentFeature !== highlight) {
            if (highlight) {
                featureOverlay.getSource().removeFeature(highlight);
            }
            if (currentFeature) {
                var featureStyle
                if (typeof clusteredFeatures == "undefined") {
					var style = currentLayer.getStyle();
					var styleFunction = typeof style === 'function' ? style : function() { return style; };
					featureStyle = styleFunction(currentFeature)[0];
				} else {
					featureStyle = currentLayer.getStyle().toString();
				}

                if (currentFeature.getGeometry().getType() == 'Point' || currentFeature.getGeometry().getType() == 'MultiPoint') {
                    var radius
					if (typeof clusteredFeatures == "undefined") {
						radius = featureStyle.getImage().getRadius();
					} else {
						radius = parseFloat(featureStyle.split('radius')[1].split(' ')[1]) + clusterLength;
					}

                    highlightStyle = new ol.style.Style({
                        image: new ol.style.Circle({
                            fill: new ol.style.Fill({
                                color: "@HIGHLIGHTFILL@"
                            }),
                            radius: radius
                        })
                    })
                } else if (currentFeature.getGeometry().getType() == 'LineString' || currentFeature.getGeometry().getType() == 'MultiLineString') {

                    var featureWidth = featureStyle.getStroke().getWidth();

                    highlightStyle = new ol.style.Style({
                        stroke: new ol.style.Stroke({
                            color: '@HIGHLIGHTFILL@',
                            lineDash: null,
                            width: featureWidth
                        })
                    });

                } else {
                    highlightStyle = new ol.style.Style({
                        fill: new ol.style.Fill({
                            color: '@HIGHLIGHTFILL@'
                        })
                    })
                }
                featureOverlay.getSource().addFeature(currentFeature);
                featureOverlay.setStyle(highlightStyle);
            }
            highlight = currentFeature;
        }
    }

    if (doHover) {
        if (popupText) {
			content.innerHTML = popupText;
            container.style.display = 'block';
            overlayPopup.setPosition(coord);
        } else {
            container.style.display = 'none';
            closer.blur();
        }
    }
};

map.on('pointermove', onPointerMove);

var popupContent = '';
var popupCoord = null;
var featuresPopupActive = false;

function updatePopup() {
    if (popupContent) {
        content.innerHTML = popupContent;
        container.style.display = 'block';
		overlayPopup.setPosition(popupCoord);
    } else {
        container.style.display = 'none';
        closer.blur();
    }
} 

function onSingleClickFeatures(evt) {
    if (doHover || sketch) {
        return;
    }
    if (!featuresPopupActive) {
        featuresPopupActive = true;
    }
    var pixel = map.getEventPixel(evt.originalEvent);
    var coord = evt.coordinate;
    var currentFeature;
    var currentFeatureKeys;
    var clusteredFeatures;
    var popupText = '<ul>';
    
    map.forEachFeatureAtPixel(pixel, function(feature, layer) {
        if (layer && feature instanceof ol.Feature && (layer.get("interactive") || layer.get("interactive") === undefined)) {
            var doPopup = false;
            for (var k in layer.get('fieldImages')) {
                if (layer.get('fieldImages')[k] !== "Hidden") {
                    doPopup = true;
                }
            }
            currentFeature = feature;
            clusteredFeatures = feature.get("features");
            if (typeof clusteredFeatures !== "undefined") {
                if (doPopup) {
                    for(var n = 0; n < clusteredFeatures.length; n++) {
                        currentFeature = clusteredFeatures[n];
                        currentFeatureKeys = currentFeature.getKeys();
                        popupText += '<li><table>';
                        popupText += '<a><b>' + layer.get('popuplayertitle') + '</b></a>';
                        popupText += createPopupField(currentFeature, currentFeatureKeys, layer);
                        popupText += '</table></li>';    
                    }
                }
            } else {
                currentFeatureKeys = currentFeature.getKeys();
                if (doPopup) {
                    popupText += '<li><table>';
                    popupText += '<a><b>' + layer.get('popuplayertitle') + '</b></a>';
                    popupText += createPopupField(currentFeature, currentFeatureKeys, layer);
                    popupText += '</table>';
                }
            }
        }
    });
    if (popupText === '<ul>') {
        popupText = '';
    } else {
        popupText += '</ul>';
    }
	
	popupContent = popupText;
    popupCoord = coord;
    updatePopup();
}

function onSingleClickWMS(evt) {
    if (doHover || sketch) {
        return;
    }
    if (!featuresPopupActive) {
        popupContent = '';
    }
    var coord = evt.coordinate;
    var viewProjection = map.getView().getProjection();
    var viewResolution = map.getView().getResolution();

    for (var i = 0; i < wms_layers.length; i++) {
        if (wms_layers[i][1] && wms_layers[i][0].getVisible()) {
            var url = wms_layers[i][0].getSource().getFeatureInfoUrl(
                evt.coordinate, viewResolution, viewProjection, {
                    'INFO_FORMAT': 'text/html',
                });
            if (url) {
                const wmsTitle = wms_layers[i][0].get('popuplayertitle');
                var ldsRoller = '<div id="lds-roller"><img class="lds-roller-img" style="height: 25px; width: 25px;"></img></div>';

                popupCoord = coord;
                popupContent += ldsRoller;
                updatePopup();

                var timeoutPromise = new Promise((resolve, reject) => {
                    setTimeout(() => {
                        reject(new Error('Timeout exceeded'));
                    }, 5000); // (5 second)
                });

                // Function to try fetch with different option
                function tryFetch(urls) {
                    if (urls.length === 0) {
                        return Promise.reject(new Error('All fetch attempts failed'));
                    }
                    return fetch(urls[0])
                        .then((response) => {
                            if (response.ok) {
                                return response.text();
                            } else {
                                throw new Error('Fetch failed');
                            }
                        })
                        .catch(() => tryFetch(urls.slice(1))); // Try next URL
                }

                // List of URLs to try
                // The first URL is the original, the second is the encoded version, and the third is the proxy
                const urlsToTry = [
                    url,
                    encodeURIComponent(url),
                    'https://api.allorigins.win/raw?url=' + encodeURIComponent(url)
                ];

                Promise.race([tryFetch(urlsToTry), timeoutPromise])
                    .then((html) => {
                        if (html.indexOf('<table') !== -1) {
                            popupContent += '<a><b>' + wmsTitle + '</b></a>';
                            popupContent += html + '<p></p>';
                            updatePopup();
                        }
                    })
                    .finally(() => {
                        setTimeout(() => {
                            var loaderIcon = document.querySelector('#lds-roller');
                            if (loaderIcon) loaderIcon.remove();
                        }, 500); // (0.5 second)
                    });
            }
        }
    }
}

map.on('singleclick', onSingleClickFeatures);
map.on('singleclick', onSingleClickWMS);

//get container
var topLeftContainerDiv = document.getElementById('top-left-container')
var bottomLeftContainerDiv = document.getElementById('bottom-left-container')
var bottomRightContainerDiv = document.getElementById('bottom-right-container')

//title
@TITLE@
//abstract
@ABSTRACT@

//geolocate
@GEOLOCATEHEAD@
@GEOLOCATE@

//measurement
@MEASURECONTROL@
@MEASURING@
@MEASURE@
@MEASUREUNIT@

//geocoder
@GEOCODINGSCRIPT@

//layer search
@LAYERSEARCH@

//scalebar
@SCALEBAR@

//layerswitcher
@LAYERSLIST@

@MAPUNITLAYERS@
@M2PX@
@GRID@

//attribution
var bottomAttribution = new ol.control.Attribution({
  collapsible: false,
  collapsed: false,
  className: 'bottom-attribution'
});
map.addControl(bottomAttribution);

var attributionList = document.createElement('li');
attributionList.innerHTML = `
	<a href="https://github.com/qgis2web/qgis2web">qgis2web</a> &middot;
	<a href="https://openlayers.org/">OpenLayers</a> &middot;
	<a href="https://qgis.org/">QGIS</a>	
`;
var bottomAttributionUl = bottomAttribution.element.querySelector('ul');
if (bottomAttributionUl) {
  bottomAttribution.element.insertBefore(attributionList, bottomAttributionUl);
}


// Disable "popup on hover" or "highlight on hover" if ol-control mouseover
var preDoHover = doHover;
var preDoHighlight = doHighlight;
var isPopupAllActive = false;
document.addEventListener('DOMContentLoaded', function() {
	if (doHover || doHighlight) {
		var controlElements = document.getElementsByClassName('ol-control');
		for (var i = 0; i < controlElements.length; i++) {
			controlElements[i].addEventListener('mouseover', function() { 
				doHover = false;
				doHighlight = false;
			});
			controlElements[i].addEventListener('mouseout', function() {
				doHover = preDoHover;
				if (isPopupAllActive) { return }
				doHighlight = preDoHighlight;
			});
		}
	}
});


//move controls inside containers, in order
    //zoom
    var zoomControl = document.getElementsByClassName('ol-zoom')[0];
    if (zoomControl) {
        topLeftContainerDiv.appendChild(zoomControl);
    }
    //geolocate
    var geolocateControl = document.getElementsByClassName('geolocate')[0];
    if (geolocateControl) {
        topLeftContainerDiv.appendChild(geolocateControl);
    }
    //measure
    var measureControl = document.getElementsByClassName('measure-control')[0];
    if (measureControl) {
        topLeftContainerDiv.appendChild(measureControl);
    }
    //geocoder
    var geocoderControl = document.getElementsByClassName('ol-geocoder')[0];
    if (geocoderControl) {
        topLeftContainerDiv.appendChild(geocoderControl);
    }
    //search layer
    var searchLayerControl = document.getElementsByClassName('search-layer')[0];
    if (searchLayerControl) {
        topLeftContainerDiv.appendChild(searchLayerControl);
    }
    //scale line
    var scaleLineControl = document.getElementsByClassName('ol-scale-line')[0];
    if (scaleLineControl) {
        scaleLineControl.className += ' ol-control';
        bottomLeftContainerDiv.appendChild(scaleLineControl);
    }
    //attribution
    var attributionControl = document.getElementsByClassName('bottom-attribution')[0];
    if (attributionControl) {
        bottomRightContainerDiv.appendChild(attributionControl);
    }