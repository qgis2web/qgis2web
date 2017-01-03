var format_airports = new ol.format.GeoJSON();
var features_airports = format_airports.readFeatures(geojson_airports, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:2964'});
var jsonSource_airports = new ol.source.Vector();
jsonSource_airports.addFeatures(features_airports);var lyr_airports = new ol.layer.Vector({
                source:jsonSource_airports, 
                style: style_airports,
                title: "airports"
            });

lyr_airports.setVisible(true);
var layersList = [lyr_airports];
lyr_airports.set('fieldAliases', {'ID': 'ID', 'fk_region': 'fk_region', 'ELEV': 'ELEV', 'NAME': 'NAME', 'USE': 'USE', });
lyr_airports.set('fieldImages', {'ID': 'TextEdit', 'fk_region': 'TextEdit', 'ELEV': 'TextEdit', 'NAME': 'TextEdit', 'USE': 'TextEdit', });
lyr_airports.set('fieldLabels', {'ID': 'no label', 'fk_region': 'no label', 'ELEV': 'no label', 'NAME': 'no label', 'USE': 'no label', });
lyr_airports.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});