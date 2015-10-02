<h1>qgis2web</h1>
<p>QGIS plugin to export your project to an OpenLayers 3 or Leaflet webmap</p>

<h2>Installation</h2>
<p>Either:</p>
<ul><li>In QGIS, select Plugins > Manage and Install Plugins...</li></ul>
<p>or:</p>
<ul><li>Download and unzip to your QGIS plugins directory</li></ul>

<h2>Current limitations</h2>
<p>Not all features are supported in both OpenLayers 3 and Leaflet export. Unsupported options are disabled in the plugin UI when you select an output format.
<ul><li>all vector layers encoded to JSON in OL3 (ie no remote WFS layers)</li>
<li>per-layer popup behaviour only supported in OL3</li>
<li>clustering only supported in Leaflet</li>
<li>no rule-based rendering</li></ul>

<h3>Per-layer options</h3>
<dl><dt>Info popup content</dt><dd>Select which fields will appear in popups when features are clicked</dd> 
<dt>Visible</dt><dd>Select whether the layer will be visible on map load. This only determines visibility - the layer will be loaded regardless of this setting</dd> 
<dt>Encode to JSON</dt><dd>If unchecked, WFS layers will remain remote WFS layers in the Leaflet map. If checked, the layer will be written to a local GeoJSON file</dd>
<dt>Cluster</dt><dd>Use Leaflet cluster plugin to cluster features</dd>
<dt>Label</dt><dd>Use layer's label as set in QGIS</dd></dl>

<h3>General options</h3>

<h4>Data export</h4>
<dl><dt>Delete unused fields</dt><dd>If not all fields are selected in "Info popup content", remove the undisplayed fields from the GeoJSON</dd>
<dt>Export folder</dt><dd>The folder where the webmap will be saved</dd> 
<dt>Mapping library location</dt><dd>Select whether to use a local copy of OL3/Leaflet, or whether to call them from their CDN</dd>
<dt>Minify GeoJSON files</dt><dd>Remove unnecessary whitespace from exported GeoJSON to reduce file size</dd>
<dt>Precision</dt><dd>Simplify geometry to reduce file size</dd></dl>

<h4>Scale/Zoom</h4>
<dl><dt>Extent</dt><dd>Either match the current QGIS view or show all contents of all layers</dd>
<dt>Max zoom level</dt><dd>How far the web map will zoom in</dd>
<dt>Min zoom level</dt><dd>How far the web map will zoom out</dd>
<dt>Restrict to extent</dt><dd>Prevent panning or zooming beyond the selected extent</dd>
<dt>Use layer scale dependent visibility</dt><dd>Respect scale dependent visibility settings from QGIS</dd></dl>

<h4>Appearance</h4>
<dl><dt>Add address search</dt><dd>Add field to allow searching for locations</dd>
<dt>Add layers list</dt><dd>Include list of layers (with legend icons, where possible)</dd>
<dt>Add measure tool</dt><dd>Include interactive measuring widget</dd>
<dt>Add scale bar</dt><dd>Include scale bar</dd>
<dt>Base layer</dt><dd>Select basemap layer</dd>
<dt>Geolocate user</dt><dd>Show user's location on map</dd>
<dt>Highlight features</dt><dd>Highlight features on mouseover</dd>
<dt>Match project CRS</dt><dd>Create web map in same projection as QGIS project</dd>
<dt>Show popups on hover</dt><dd>Show popups when mouse hovers over feature</dd>
<dt>Template</dt><dd>Select HTML template for web map</dd></dl>

<h2>Credits</h2>
<p>qgis2web is fundamentally a merge of Victor Olaya's qgis-ol3 and Riccardo Klinger's qgis2leaf. It would not exist without their work. Thank you, gentlemen.</p>

<ul><li>github.com/volaya/</li>
<li>github.com/riccardoklinger/</li></ul>
