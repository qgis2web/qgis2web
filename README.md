[![GitHub version](https://badge.fury.io/gh/tomchadwin%2Fqgis2web.svg)](https://badge.fury.io/gh/tomchadwin%2Fqgis2web)
[![Build Status](https://travis-ci.org/tomchadwin/qgis2web.svg?branch=master)](https://travis-ci.org/tomchadwin/qgis2web)
[![Coverage Status](https://coveralls.io/repos/github/tomchadwin/qgis2web/badge.svg?branch=master)](https://coveralls.io/github/tomchadwin/qgis2web?branch=master)
[![Join the chat at https://gitter.im/tomchadwin/qgis2web](https://badges.gitter.im/tomchadwin/qgis2web.svg)](https://gitter.im/tomchadwin/qgis2web?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
<h1>qgis2web</h1>
<p>QGIS plugin to export your project to an OpenLayers 3 or Leaflet webmap. No
server-side software required.</p>

<h2>Installation</h2>
<ul>
    <li>In QGIS, select <code>Plugins > Manage and Install Plugins...</code></li>
</ul>
<p>or:</p>
<ul>
    <li>Download and unzip to your QGIS plugins directory</li>
</ul>

<h2>Usage</h2>
<p>Prepare your map as far as possible in QGIS, as you want it to appear in
your webmap. Specific tasks you can carry out to improve your webmap include:
</p>
<ul>
    <li>Set your project title, and background and highlight colours in 
        <code>Project > Project Properties...</code></li>
    <li>Give your layers human-friendly names in the <code>Layers Panel</code>
    </li>
    <li>Give your layer columns human friendly names via <code>Layer >
        Properties > Fields > Alias</code></li>
    <li>Hide the columns you don't want to appear in your popups by changing
        their Edit widget to "Hidden"</li>
    <li>If any of your fields contain image filenames, change their Edit
        widget to "Photo" to have the images appear in popups</li>
    <li>Style your layers, and set their scale-dependent visibility, if
        required</li>
</ul>
<p>Run qgis2web from the Web menu, or via its icon. If required, choose a
basemap from the list below the preview pane, and click "Update preview".
CTRL/CMD-click for multiple basemaps or to deselect a basemap.</p>
<p>The top-left pane lets you set options for each layer in your map. The
bottom-left pane sets overall options. All options are written to your QGIS
project, so save your proejct if you want to keep these settings.</p>

<h2>Current limitations</h2>
<p>QGIS, OpenLayers 3, and Leaflet are all different mapping technologies.
This means that their respective functionality differs in many ways. qgis2web
does its best to interpret a QGIS project and to export HTML, Javascript, and
CSS to create a web map as close to the QGIS project as possible.</p>
<p>However, many elements of a QGIS project cannot be reproduced, and many are
only possible in <em>either</em> OpenLayers 3 <em>or</em> Leaflet. qgis2web
tries its best to produce a publish-ready map, but you can always manually edit
the output code to achieve what qgis2web cannot.</p>
<ul>
    <li>no rule-based rendering</li>
    <li>SVG point markers sometimes do not appear in the preview
        pane, but work when the map is exported</li>
    <li>OpenLayers 3 address search does not appear in the preview
        pane, but works when the map is exported</li>
    <li>Leaflet maps only use each symbol's first symbol layer</li>
    <li>in OL3 maps, only single rendered points cluster, not categorized
        or graduated</li>
    <li>rasters are exported unstyled</li>
    <li>line style (dashed/dotted) does not appear in OL3 preview, but works in
        export</li>
    <li>Leaflet cannot label lines and polygons, only points</li>
    <li>only a single 2.5d layer will render per map</li>
    <li>2.5d layers only appear when zoomed in to building scales</li>
</ul>

<h3>Layer options</h3>
<dl>
    <dt>Popup fields</dt>
        <dd>Specify how each field will be labelled in popups</dd> 
    <dt>Visible</dt>
        <dd>Select whether the layer will be visible on map load. This only
            determines visibility - the layer will be loaded regardless of this
            setting</dd> 
    <dt>Encode to JSON</dt>
        <dd>If unchecked, WFS layers will remain remote WFS layers in the
            webmap. If checked, the layer will be written to a local GeoJSON
            file</dd>
    <dt>Cluster</dt>
        <dd>Cluster point features</dd>
</dl>

<h3>General options</h3>

<h4>Data export</h4>
<dl>
    <dt>Export folder</dt>
        <dd>The folder where the webmap will be saved</dd> 
    <dt>Mapping library location</dt>
        <dd>Select whether to use a local copy of OL3/Leaflet, or whether to
            call the library from its CDN</dd>
    <dt>Minify GeoJSON files</dt>
        <dd>Remove unnecessary whitespace from exported GeoJSON to reduce file
            size</dd>
    <dt>Precision</dt>
        <dd>Simplify geometry to reduce file size</dd>
</dl>

<h4>Scale/Zoom</h4>
<dl>
    <dt>Extent</dt>
        <dd>Either match the current QGIS view or show all contents of all
            layers (only local GeoJSON and rasters, not WFS/WMS)</dd>
    <dt>Max zoom level</dt>
        <dd>How far the webmap will zoom in</dd>
    <dt>Min zoom level</dt>
        <dd>How far the webmap will zoom out</dd>
    <dt>Restrict to extent</dt>
        <dd>Prevent panning or zooming beyond the selected extent</dd>
</dl>

<h4>Appearance</h4>
<dl>
    <dt>Add address search</dt>
        <dd>Add field to allow searching for locations (geocode)</dd>
    <dt>Add layers list</dt>
        <dd>Include list of layers (with legend icons, where possible)</dd>
    <dt>Add measure tool</dt>
        <dd>Include interactive measuring widget</dd>
    <dt>Geolocate user</dt>
        <dd>Show user's location on map</dd>
    <dt>Highlight on hover</dt>
        <dd>Highlight features on mouseover</dd>
    <dt>Layer search</dt>
        <dd>Add option to search for values in layer field values</dd>
    <dt>Match project CRS</dt>
        <dd>Create webmap in same projection as QGIS project, otherwise the
        webmap is projected in EPSG:3857</dd>
    <dt>Show popups on hover</dt>
        <dd>Show popups when mouse hovers over features</dd>
    <dt>Template</dt>
        <dd>Select HTML template for webmap - add your own templates to the
            /qgis2web/templates directory in your .qgis2 folder</dd>
</dl>

<h2>Reporting bugs</h2>
<p>Please report any problems you have with qgis2web. Without this feedback, I
am often completely unaware that a problem exists. To ensure no time or effort
is wasted in bug reporting, please follow these steps:</p>
<ol>
    <li>Make sure you are using the latest release of qgis2web</li>
    <li>Check the issues on Github to see whether the bug has already been
        reported, and if so, read through all the comments on the issue, and
        add any additional information from your experience of the bug</li>
    <li>Make sure you can reproduce the bug reliably</li>
    <li>Reduce the complexity of your bug conditions as far as you can,
        especially by reducing the number of layers, ideally to one</li>
    <li>Raise a Github issue, including:
    <ul>
        <li>only one bug per Github issue</li>
        <li>the qgis2web version (or make it clear you are using Github master
            branch)</li>
        <li>any Python error text/stack trace which occurs</li>
        <li>browser JS console errors - press F12 in qgis2web to open the 
            developer toolbar and find the console</li>
        <li>screenshot of your settings</li>
        <li>screenshot of the output</li>
        <li>a link to the data you used, if possible</li>
    </ul></li>
</ol>
<p>The stability of qgis2web relies on your bug reports, so please keep them
coming.</p>

<h2>Credits</h2>
<p>qgis2web is fundamentally a merge of Victor Olaya's qgis-ol3 and Riccardo
Klinger's qgis2leaf. It would not exist without their work. Thank you,
gentlemen. Thanks are also very much due to Paolo Cavallini, who suggested
and supported the merge.</p>
<ul>
    <li>@volaya</li>
    <li>@riccardoklinger</li>
    <li>@pcav</li>
</ul>

<p>Obviously, qgis2web could not exist without the following monumental
software:</p>
<ul>
    <li>QGIS</li>
    <li>OpenLayers 3</li>
    <li>Leaflet</li>
</ul>

<p>Thanks are also due for major code contributions to:</p>
<ul>
    <li>@akbargumbira</li>
    <li>@lucacasagrande</li>
    <li>@walkermatt</li>
    <li>@boesiii</li>
    <li>@ThomasG77</li>
</ul>

<p>In addition, the following libraries have been used:</p>
<ul>
    <li>ol3-layerswitcher, by @walkermatt</li>
    <li>Autolinker.js, by @gregjacobs</li>
    <li>requestAnimationFrame polyfill, by @paulirish</li>
    <li>Function.prototype.bind polyfill, by @mozilla</li>
    <li>Leaflet.draw, by @jacobtoye</li>
    <li>Leaflet.label, by @jacobtoye</li>
    <li>Leaflet.Locate, by @domoritz</li>
    <li>Leaflet.markercluster, by @danzel</li>
    <li>Leaflet.MeasureControl, by @makinacorpus</li>
    <li>leaflet-hash, by @mlevans</li>
    <li>Proj4js, by @madair, @calvinmetcalf, and other</li>
    <li>Proj4Leaflet, by @kartena</li>
    <li>Leaflet.search, by @stefanocudini</li>
    <li>ol3-search-layer, by @ThomasG77</li>
    <li>Leaflet.heat, by @mourner</li>
    <li>OSMBuildings, by @kekscom</li>
</ul>
