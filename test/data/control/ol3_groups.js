var format_airports0 = new ol.format.GeoJSON();
var features_airports0 = format_airports0.readFeatures(json_airports0, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_airports0 = new ol.source.Vector({
    attributions: [new ol.Attribution({html: '<a href=""></a>'})],
});
jsonSource_airports0.addFeatures(features_airports0);var lyr_airports0 = new ol.layer.Vector({
                source:jsonSource_airports0, 
                style: style_airports0,
                title: "airports"
            });
var group_group1 = new ol.layer.Group({
                                layers: [lyr_airports0],
                                title: "group1"});

lyr_airports0.setVisible(true);
var layersList = [group_group1];
lyr_airports0.set('fieldAliases', {'ID': 'ID', 'fk_region': 'fk_region', 'ELEV': 'ELEV', 'NAME': 'NAME', 'USE': 'USE', });
lyr_airports0.set('fieldImages', {'ID': 'TextEdit', 'fk_region': 'TextEdit', 'ELEV': 'TextEdit', 'NAME': 'TextEdit', 'USE': 'TextEdit', });
lyr_airports0.set('fieldLabels', {});
lyr_airports0.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});