#qgis2web
A plugin to export a QGIS map to an OpenLayers 3 or Leaflet webmap

##Installation
* In QGIS, select Plugins > Manage and Install Plugins...
or
* Download and unzip to your QGIS plugins directory

##Current limitations
Not all features are supported in both OpenLayers 3 and Leaflet export. Unsupported options are disabled in the plugin UI when you select an output format.
+ all vector layers encoded to JSON in OL3 (ie no remote WFS layers)
+ per-layer popup behaviour only supported in OL3
+ clustering only supported in Leaflet
+ scale-dependent visibility only supported in OL3