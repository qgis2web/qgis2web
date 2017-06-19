var format_airports0 = new ol.format.GeoJSON();
var features_airports0 = format_airports0.readFeatures(json_airports0, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_airports0 = new ol.source.Vector({
    attributions: [new ol.Attribution({html: '<a href=""></a>'})],
});
jsonSource_airports0.addFeatures(features_airports0);var lyr_airports0 = new ol.layer.Heatmap({
                source:jsonSource_airports0, 
                radius: 10 * 2,
                gradient: ['#ffffff', '#000000'],
                blur: 15,
                shadow: 250,
                title: 'airports'
            });

lyr_airports0.setVisible(true);
var layersList = [lyr_airports0];
lyr_airports0.set('fieldAliases', {'ID': 'ID', 'fk_region': 'fk_region', 'ELEV': 'ELEV', 'NAME': 'NAME', 'USE': 'USE', });
lyr_airports0.set('fieldImages', {'ID': 'TextEdit', 'fk_region': 'TextEdit', 'ELEV': 'TextEdit', 'NAME': 'TextEdit', 'USE': 'TextEdit', });
lyr_airports0.set('fieldLabels', {'ID': 'no label', 'fk_region': 'no label', 'ELEV': 'no label', 'NAME': 'no label', 'USE': 'no label', });
lyr_airports0.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});