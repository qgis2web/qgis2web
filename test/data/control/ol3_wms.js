var lyr_GBRBGS1625kBedrockLithology0 = new ol.layer.Tile({
                            source: new ol.source.TileWMS(({
                              url: "http://ogc.bgs.ac.uk/cgi-bin/BGS_Bedrock_and_Superficial_Geology/wms?",
    attributions: [new ol.Attribution({html: '<a href=""></a>'})],
                              params: {
                                "LAYERS": "GBR_BGS_625k_BLT",
                                "TILED": "true",
                                "VERSION": "1.3.0"},
                            })),
                            title: "GBR BGS 1:625k Bedrock Lithology",
                            opacity: 1.000000,
                            
                            
                          });

lyr_GBRBGS1625kBedrockLithology0.setVisible(true);
var layersList = [lyr_GBRBGS1625kBedrockLithology0];
