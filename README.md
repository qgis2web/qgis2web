<h1>qgis2web</h1>
<p>QGIS plugin to export your project to an OpenLayers 3 or Leaflet webmap</p>

## Installation
- In QGIS, select Plugins > Manage and Install Plugins...
or
- Download and unzip to your QGIS plugins directory

## Current limitations
<p>Not all features are supported in both OpenLayers 3 and Leaflet export. Unsupported options are disabled in the plugin UI when you select an output format.
- all vector layers encoded to JSON in OL3 (ie no remote WFS layers)
- per-layer popup behaviour only supported in OL3
- clustering only supported in Leaflet
- no rule-based rendering

### Per-layer options
**Info popup content**: Select which fields will appear in popups when features are clicked.  
**Visible**: Select whether the layer will be visible on map load. This only determines visibility - the layer will be loaded regardless of this setting.  
**Encode to JSON**: If unchecked, WFS layers will remain remote WFS layers in the Leaflet map. If checked, the layer will be written to a local GeoJSON file.  
**Cluster**: Use Leaflet cluster plugin to cluster features.  
**Label**: Use layer's label as set in QGIS.

### General options

#### Data export
**Delete unused fields**: If not all fields are selected in "Info popup content", remove the undisplayed fields from the GeoJSON.  
**Export folder**: The folder where the webmap will be saved.  
**Mapping library location**: Select whether to use a local copy of OL3/Leaflet, or whether to call them from their CDN.  
**Minify GeoJSON files**: Remove unnecessary whitespace from exported GeoJSON to reduce file size.  
**Precision**: Simplify geometry to reduce file size.  

#### Scale/Zoom
**Extent**: Either match the current QGIS view or show all contents of all layers.  
**Max zoom level**: How far the web map will zoom in.  
**Min zoom level**: How far the web map will zoom out.  
**Restrict to extent**: Prevent panning or zooming beyond the selected extent.  
**Use layer scale dependent visibility**: Respect scale dependent visibility settings from QGIS.  

#### Appearance
**Add address search**: Add field to allow searching for locations.  
**Add layers list**: Include list of layers (with legend icons, where possible).  
**Add measure tool**: Include interactive measuring widget.  
**Add scale bar**: Include scale bar.  
**Base layer**: Select basemap layer.  
**Geolocate user**: Show user's location on map.  
**Highlight features**: Highlight features on mouseover.  
**Match project CRS**: Create web map in same projection as QGIS project.  
**Show popups on hover**: Show popups when mouse hovers over feature.  
**Template**: Select HTML template for web map.