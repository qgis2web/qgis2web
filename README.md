[![Build Status](https://travis-ci.org/tomchadwin/qgis2web.svg?branch=master)](https://travis-ci.org/tomchadwin/qgis2web)
[![Coverage Status](https://coveralls.io/repos/github/tomchadwin/qgis2web/badge.svg?branch=master)](https://coveralls.io/github/tomchadwin/qgis2web?branch=master)
[![Join the chat at https://gitter.im/tomchadwin/qgis2web](https://badges.gitter.im/tomchadwin/qgis2web.svg)](https://gitter.im/tomchadwin/qgis2web?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
<h1>qgis2web</h1>
<p>A QGIS plugin to export your project to an OpenLayers 3 or Leaflet webmap. No
server-side software required.</p>

<h2>Scope</h2>
<p>qgis2web interprets a QGIS project and  exports HTML, Javascript, and CSS to
create a web map as close to the QGIS project as possible. QGIS, OpenLayers, and
Leaflet differ in many ways. Scope is limited to shared functionality that
exists in all three of the systems. The output code could be manually edited to
achieve more complicated functionality.</p>

<p>To share the output, you will need simple web hosting. This is outside of the
scope of this plugin.</p>

<h2>Installation</h2>
<ul>
    <li>In QGIS, select <code>Plugins > Manage and Install Plugins...</code></li>
</ul>
<p>or:</p>
<ul>
    <li>Download and unzip to your QGIS plugins directory</li>
</ul>

<h2>Usage</h2>
<p>Prepare your map in QGIS as you want it to appear in your webmap.</p>

You could:
<ul>
    <li>Set a project title in <code>Project > Project Properties...</code></li>
    <li>Set background and highlight colours in <code>Project > Project
        Properties...</code></li>
    <li>Choose a basemap from the list under the preview pane, and click <code>
        Update preview</code></li>
    <li>Select multiple basemaps or deselect a basemap with <code>CTRL/CMD-click
        </code></li>
    <li>Give your layers human-friendly names in the <code>Layers Panel</code>
    </li>
    <li>Give your layer columns human-friendly names via <code>Layer >
        Properties > Fields > Alias</code></li>
    <li>Hide columns that you don't want to appear in popups by changing their
        <code>Edit widget</code> to <code>Hidden</code></li>
    <li>Style your layers</li>
    <li>Set scale-dependent visibility of layers</li>
</ul>

<p>Run qgis2web from the <code>Web</code> menu or via its icon.</p>

<p>The top-left pane sets options for each map layer. The bottom-left pane sets overall options. These are written to your QGIS project, so save your project if you want to keep them.</p>

<h3>Layer options</h3>
<dl>
    <dt>Info popup content</dt>
        <dd>Select which fields will appear in popups when features are clicked
        </dd>
    <dt>Visible</dt>
        <dd>Select whether the layer will be visible on map load. This only
            determines visibility - the layer will be loaded regardless of this
            setting</dd>
    <dt>Encode to JSON</dt>
        <dd>If unchecked, WFS layers will remain remote WFS layers in the
            webmap. If checked, the layer will be written to a local GeoJSON
            Javascript file</dd>
    <dt>Cluster</dt>
        <dd>Cluster point features</dd>
</dl>

<h3>General options</h3>

<h4>Data export</h4>
<dl>
    <dt>Delete unused fields</dt>
        <dd>If "show all attributes" is not selected in "Info popup content",
            remove the undisplayed fields from the GeoJSON - helps to reduce
            file size</dd>
    <dt>Export folder</dt>
        <dd>The folder where the webmap will be saved</dd>
    <dt>Mapping library location</dt>
        <dd>Select whether to use a local copy of OL3/Leaflet, or whether to
            call the library from its CDN</dd>
    <dt>Minify GeoJSON files</dt>
        <dd>Remove unnecessary whitespace from exported GeoJSON to reduce file
            size</dd>
    <dt>Precision</dt>
        <dd>Reduce geometry accuracy to reduce file size</dd>
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
    <dt>Add scale bar</dt>
        <dd>Include dynamic scale bar</dd>
    <dt>Geolocate user</dt>
        <dd>Show user's location on map</dd>
    <dt>Highlight on hover</dt>
        <dd>Highlight features on mouseover</dd>
    <dt>Match project CRS</dt>
        <dd>Create webmap in same projection as QGIS project, otherwise the
            webmap is projected in EPSG:3857</dd>
    <dt>Show popups on hover</dt>
        <dd>Show popups when mouse hovers over features</dd>
    <dt>Template</dt>
        <dd>Select HTML template for webmap - add your own templates to the
            /qgis2web/templates directory in your .qgis2 folder</dd>
</dl>

<h2>Current limitations</h2>
<ul>
    <li>no rule-based rendering
    <li>SVG point markers sometimes do not appear in the preview pane, but work
        when the map is exported</li>
    <li>Leaflet maps only use each symbol's first symbol layer</li>
    <li>in OL3 maps, only single rendered points cluster, not categorized or
        graduated</li>
    <li>rasters are exported unstyled</li>
    <li>line style (dashed/dotted) does not appear in OL3 preview, but works in
        export</li>
    <li>Leaflet can label points, but cannot label lines and polygons</li>
    <li>only a single 2.5d layer will render per map</li>
    <li>2.5d layers only appear when zoomed in to building scales</li>
</ul>

<h2>Reporting bugs</h2>
<p>Please report any problems you have with qgis2web as we may be unaware that a problem exists. Save time and effort by following these steps:</p>
<ol>
    <li>Make sure you are using the latest release of qgis2web</li>
    <li>Check the issues on Github to see whether the bug has already been reported, and if so, read through all the comments on the issue, and add any additional information from your experience of the bug</li>
    <li>Make sure you can reproduce the bug reliably</li>
    <li>Reduce the complexity of your bug conditions as far as you can, especially by reducing the number of layers, ideally to one</li>
    <li>Raise a Github issue, including:
        <ul>
            <li>the qgis2web version (or make it clear if you are using the
                Github master branch)</li>
            <li>python error text/stack trace which occurs</li>
            <li>browser JS console errors - press F12 in qgis2web to open the
                developer toolbar and find the console</li>
            <li>screenshot of your settings</li>
            <li>screenshot of the output</li>
            <li>a link to the data you used, if possible</li>
        </ul></li>
</ol>

<p>The stability of qgis2web relies on your bug reports, so please keep them
coming.</p>

<h2>Development</h2>
<p>qgis2web is largely developed by Tom Chadwin with significant contributions
from a few others. Please, please do contribute, as there is so much more to do.
</p>

<p>There is basic feature parity between Leaflet and OL3 exports. The overall
direction of the plugin is that any new features should be implemented in both
formats.</p>

<p>The core philosophy of the plugin is: don’t get the plugin to do anything
which QGIS can already do. Keep the focus on producing good-quality maps,
reproducing as much from QGIS as possible, rather than adding additional
functionality.</p>

<h3>Coding guidelines</h3>
<ul>
    <li>Comply with <a href="https://www.python.org/dev/peps/pep-0008/">PEP8</a>
    </li>
    <li>Remove <code>print</code> statements before making a pull request</li>
    <li>Run the tests, and don’t break them</li>
    <li>Anything which alters the output for the basic tests will mean updating
        the control files in <code>/test/data/control</code></li>
    <li>Write tests for new functionality</li>
    <li>Don't introduce a new client-side library for something which can easily
        be done without it (I'm looking at you jQuery!)</li>
</ul>

<h3>Other improvements required</h3>
<ul>
    <li>Improve code quality/refactor</li>
    <li>Write tests for more functionality - coverage is currently very low</li>
</ul>

<h2>Testing</h2>
<p>Commits and pull requests are automatically tested by Travis. The tests are
in <code>/test</code>, specifically <code>/test/test_qgis2web_dialog.py</code>.
If you want to run these tests locally on Linux, do the following to prepare
(assumes Ubuntu or derivative):</p>

<p>Install the pip Python package manager</p>
<pre><code>
apt-get install python-pip
</code></pre>

<p>Install nose and coverage which are used to run the tests</p>
<pre><code>
pip install nose
pip install coverage
</code></pre>

<p>Change to the directory which contains the plugin code</p>
<pre><code>
cd ~/.qgis2/python/plugins/qgis2web
</code></pre>

<p>Set up the environment specifying the prefix path under which QGIS is
installed (commonly /usr or /usr/local).</p>
<pre><code>
source scripts/run-env-linux.sh /usr
</code></pre>

<p>Set the QGIS_REPO environment variable to match the QGIS version you are
using:</p>
<ul>
    <li>http://qgis.org/debian-ltr for long term support version</li>
    <li>http://qgis.org/debian for current version</li>
    <li>http://qgis.org/debian-nightly for current master / nightly version</li>
</ul>
<pre><code>
export QGIS_REPO=http://qgis.org/debian-ltr
</code></pre>

<p>Run the tests with:</p>
<pre><code>
make test
</code></pre>

<h3>Mac OS X</h3>
<p>qgis can be fully installed using homebrew
https://github.com/OSGeo/homebrew-osgeo4mac.</p>

<p>There is a shell script to set the qgis paths:</p>
<pre><code>
pip install nose
pip install coverage
source scripts/run-env-osx-homebrew.sh
make test
</code></pre>

<h3>virtualenv</h3>
<p>There may be a problem using virtualenv with pyqgis (or someone might get it
working and tell us how). After 'import qgis' there is an error retrieving
sip.</p>

<h3>Untested functionality</h3>
<ul>
    <li>rasters</li>
    <li>labels</li>
    <li>rule-based renderer</li>
    <li>SVG markers</li>
    <li>polygon border style "No pen"</li>
    <li>polygon fill style "No brush"</li>
    <li>line cap/join styles</li>
    <li>change export folder via mouse click</li>
    <li>save settings</li>
    <li>click layer popup combo</li>
    <li>unchecked layers initially collapsed and non-visible</li>
    <li>restore saved project/layer settings</li>
    <li>open dev console</li>
    <li>WFS encode to JSON</li>
    <li>close qgis2web</li>
    <li>Leaflet polygon outline: simple line</li>
    <li>Leaflet line style (dot/dash)</li>
    <li>Leaflet line width > 1</li>
    <li>Leaflet categorized clusters</li>
    <li>Leaflet graduated clusters</li>
    <li>Leaflet WMS</li>
    <li>Leaflet WFS clusters</li>
    <li>Leaflet JSON non-point popups</li>
    <li>Leaflet scale-dependent visibility</li>
    <li>Leaflet match CRS</li>
    <li>Leaflet basemaps</li>
    <li>Leaflet basemaps + layers list</li>
    <li>Leaflet cluster + layers list</li>
    <li>Leaflet raster + layers list</li>
    <li>Leaflet project title</li>
    <li>Leaflet highlight + popups on hover</li>
    <li>Leaflet categorized on non-string column</li>
    <li>Leaflet categorized JSON point without popup</li>
    <li>Leaflet custom popup contents via <code>html_prov</code></li>
    <li>Leaflet export</li>
    <li>OL3 measure - imperial units</li>
    <li>OL3 blank template value</li>
    <li>OL3 layer groups</li>
    <li>OL3 canvas extent</li>
    <li>OL3 WFS cluster</li>
    <li>OL3 layer transparency</li>
</ul>

<p>If you have time to write tests for any of this then it will benefit the
plugin hugely. Make sure you delete any tests from this list. Some of the items
above I don't even know how to test...</p>

<h2>Credits</h2>
<p>qgis2web is fundamentally a merge of Victor Olaya's qgis-ol3 and Riccardo
Klinger's qgis2leaf. It would not exist without their work. Thank you,
gentlemen. Thanks are also very much due to Paolo Cavallini who suggested and
supported the merge.</p>
<ul>
    <li>@volaya</li>
    <li>@riccardoklinger</li>
    <li>@pcav</li>
</ul>

<p>qgis2web could not exist without the monumental software:</p>
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
</ul>

<p>The following libraries have been used:</p>
<ul>
    <li>ol3-layerswitcher by @walkermatt</li>
    <li>Autolinker.js by @gregjacobs</li>
    <li>requestAnimationFrame polyfill by @paulirish</li>
    <li>Function.prototype.bind polyfill by @mozilla</li>
    <li>Leaflet.draw and Leaflet.label by @jacobtoye</li>
    <li>Leaflet.markercluster by @danzel</li>
    <li>Leaflet.MeasureControl by @makinacorpus</li>
    <li>leaflet-hash by @mlevans</li>
    <li>Proj4js by @madair, @calvinmetcalf, and others</li>
    <li>Proj4Leaflet by @kartena</li>
    <li>OSMBuildings by @kekscom</li>
</ul>
