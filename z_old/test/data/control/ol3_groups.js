var wms_layers = [];

var format_airports_0 = new ol.format.GeoJSON();
var features_airports_0 = format_airports_0.readFeatures(json_airports_0, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_airports_0 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_airports_0.addFeatures(features_airports_0);
var lyr_airports_0 = new ol.layer.Vector({
                declutter: true,
                source:jsonSource_airports_0, 
                style: style_airports_0,
                interactive: true,
                title: '<img src="styles/legend/airports_0.png" /> airports'
            });
var group_group1 = new ol.layer.Group({
                                layers: [lyr_airports_0,],
                                title: "group1"});

lyr_airports_0.setVisible(true);
var layersList = [group_group1];
lyr_airports_0.set('fieldAliases', {'ID': 'ID', 'fk_region': 'fk_region', 'ELEV': 'ELEV', 'NAME': 'NAME', 'USE': 'USE', });
lyr_airports_0.set('fieldImages', {'ID': '', 'fk_region': '', 'ELEV': '', 'NAME': '', 'USE': '', });
lyr_airports_0.set('fieldLabels', {});
lyr_airports_0.on('precompose', function(evt) {
    evt.context.globalCompositeOperation = 'normal';
});