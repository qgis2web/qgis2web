@MEASURECONTROL@
      var container = document.getElementById('popup');
      var content = document.getElementById('popup-content');
      var closer = document.getElementById('popup-closer');
      closer.onclick = function() {
        container.style.display = 'none';
        closer.blur();
        return false;
      };
      var overlayPopup = new ol.Overlay({
        element: container
      });

      var map = new ol.Map({
        controls: ol.control.defaults().extend([
          @CONTROLS@
        ]),
        target: document.getElementById('map'),
        renderer: 'canvas',
        overlays: [overlayPopup],
        layers: layersList,
        view: new ol.View({
          @VIEW@
        })
      });
      map.getView().fit(@BOUNDS@, map.getSize());

      var NO_POPUP = 0
      var ALL_FIELDS = 1

      @POPUPLAYERS@

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

      var highlight;
      var onPointerMove = function(evt) {
        if (!doHover && !doHighlight){
          return;
        }
        var pixel = map.getEventPixel(evt.originalEvent);
        var coord = evt.coordinate;
        var popupField;
        var popupText = '';
        var currentFeature;
        var currentFeatureKeys;
        map.forEachFeatureAtPixel(pixel, function(feature, layer) {
          currentFeature = feature;
          currentFeatureKeys = currentFeature.getKeys();
          var field = popupLayers[layersList.indexOf(layer) - 1];
          if (field == NO_POPUP){          
          }
          else if (field == ALL_FIELDS){
            popupText = '<table>';
            for ( var i=0; i<currentFeatureKeys.length;i++) {
                if (currentFeatureKeys[i] != 'geometry') {
                    popupField = '<th>' + currentFeatureKeys[i] + ':</th><td>'+ currentFeature.get(currentFeatureKeys[i]) + '</td>';
                    popupText = popupText + '<tr>' + popupField + '</tr>';
                }
            }
            popupText = popupText + '</table>';
          }
          else{
            var value = feature.get(field);
            if (value){
              popupText = '<strong>' + field + ':</strong> ' + value;
            }  
          }@MEASURING@          
        });

        if (doHighlight){
          if (currentFeature !== highlight) {
            if (highlight) {
              featureOverlay.getSource().removeFeature(highlight);
            }
            if (currentFeature) {
              if (currentFeature.getGeometry().getType() == 'Point') {
                highlightStyle = new ol.style.Style({
                image: new ol.style.Circle({
                  fill: new ol.style.Fill({
                    color: "@HIGHLIGHTFILL@"
                  })
                })
               })
              } else {
                highlightStyle = new ol.style.Style({
                  fill: new ol.style.Fill({
                    color: '@HIGHLIGHTFILL@'
                  }),
                })
              }
              featureOverlay.getSource().addFeature(currentFeature);
              featureOverlay.setStyle(highlightStyle);
            }
            highlight = currentFeature;
          }
        }

        if (doHover){
          if (popupText) {
            overlayPopup.setPosition(coord);
            content.innerHTML = popupText;
            container.style.display = 'block';        
          } else {
            container.style.display = 'none';
            closer.blur();
          }
        }
      };

      var onSingleClick = function(evt) {
        if (doHover){
          return;
        }
        var pixel = map.getEventPixel(evt.originalEvent);
        var coord = evt.coordinate;
        var popupField;
        var popupText = '';
        var currentFeature;
        var currentFeatureKeys;
        map.forEachFeatureAtPixel(pixel, function(feature, layer) {
          currentFeature = feature;
          currentFeatureKeys = currentFeature.getKeys();
          var field = popupLayers[layersList.indexOf(layer) - 1];
          if (field == NO_POPUP){          
          }
          else if (field == ALL_FIELDS){
            popupText = '<table>';
            for ( var i=0; i<currentFeatureKeys.length;i++) {
                if (currentFeatureKeys[i] != 'geometry') {
                    popupField = '<th>' + currentFeatureKeys[i] + ':</th><td>' + Autolinker.link(currentFeature.get(currentFeatureKeys[i])) + '</td>';
                    popupText = popupText + '<tr>' + popupField + '</tr>';
                }
            }
            popupText = popupText + '</table>';
          }
          else{
            var value = feature.get(field);
            if (value){
              popupText = '<strong>' + field + ':</strong> '+ value;
            }  
          }          
        });

        if (popupText) {
            overlayPopup.setPosition(coord);
            content.innerHTML = popupText;
            container.style.display = 'block';        
        } else {
          container.style.display = 'none';
          closer.blur();
        }
      };

      map.on('pointermove', function(evt) {
        onPointerMove(evt);
      });
      map.on('singleclick', function(evt) {
        onSingleClick(evt);
      });@MEASURE@@GEOLOCATE@@GEOCODINGSCRIPT@