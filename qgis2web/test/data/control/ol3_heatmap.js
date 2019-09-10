var wms_layers = [];

var format_airports_0 = new ol.format.GeoJSON();
var features_airports_0 = format_airports_0.readFeatures(json_airports_0, 
            {dataProjection: 'EPSG:4326', featureProjection: 'EPSG:3857'});
var jsonSource_airports_0 = new ol.source.Vector({
    attributions: ' ',
});
jsonSource_airports_0.addFeatures(features_airports_0);
var lyr_airports_0 = new ol.layer.Heatmap({
                declutter: true,
                source:jsonSource_airports_0, 
                radius: 10 * 2,
                gradient: ['#ffffff', '#000000'],
                blur: 15,
                shadow: 250,
                title: 'airports'
            });

lyr_airports_0.setVisible(true);
var layersList = [lyr_airports_0];
