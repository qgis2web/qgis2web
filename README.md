[![Build Status](https://travis-ci.org/tomchadwin/qgis2web.svg?branch=master)](https://travis-ci.org/tomchadwin/qgis2web)
[![Coverage Status](https://coveralls.io/repos/github/tomchadwin/qgis2web/badge.svg?branch=master)](https://coveralls.io/github/tomchadwin/qgis2web?branch=master)
[![Join the chat at https://gitter.im/tomchadwin/qgis2web](https://badges.gitter.im/tomchadwin/qgis2web.svg)](https://gitter.im/tomchadwin/qgis2web?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
qgis2web
========
A QGIS plugin to export your project to an OpenLayers 3 or Leaflet webmap. No server-side software required.

Scope
-----
qgis2web interprets a QGIS project and  exports HTML, Javascript, and CSS to create a web map as close to the QGIS project as possible. QGIS, OpenLayers, and Leaflet differ in many ways. Scope is limited to shared functionality that exists in all three of the systems. The output code could be manually edited to achieve more complicated functionality.

To share the output, you will need simple web hosting. This is outside of the scope of this plugin.

Installation
------------
* In QGIS, select <code>Plugins > Manage and Install Plugins...</code>

or:

* Download and unzip to your QGIS plugins directory

Usage
-----
Prepare your map in QGIS as you want it to appear in your webmap.

You could:
* Set a project title in <code>Project > Project Properties...</code>
* Set background and highlight colours in <code>Project > Project Properties...</code>
* Choose a basemap from the list under the preview pane, and click <code>Update preview</code>
* Select multiple basemaps or deselect a basemap with <code>CTRL/CMD-click</code>
* Give your layers human-friendly names in the <code>Layers Panel</code>
* Give your layer columns human-friendly names via <code>Layer > Properties > Fields > Alias</code>
* Hide columns that you don't want to appear in popups by changing their <code>Edit widget</code> to <code>Hidden</code>
* Style your layers
* Set scale-dependent visibility of layers

Run qgis2web from the <code>Web</code> menu or via its icon.

The top-left pane sets options for each map layer. The bottom-left pane sets overall options. These are written to your QGIS project, so save your project if you want to keep them.

### Layer options
<dl>
    <dt>Info popup content</dt>
        <dd>Select which fields will appear in popups when features are clicked</dd>
    <dt>Visible</dt>
        <dd>Select whether the layer will be visible on map load. This only determines visibility - the layer will be loaded regardless of this setting</dd>
    <dt>Encode to JSON</dt>
        <dd>If unchecked, WFS layers will remain remote WFS layers in the webmap. If checked, the layer will be written to a local GeoJSON Javascript file</dd>
    <dt>Cluster</dt>
        <dd>Cluster point features</dd>
</dl>

### General options

#### Data export
<dl>
    <dt>Delete unused fields</dt>
        <dd>If "show all attributes" is not selected in "Info popup content", remove the undisplayed fields from the GeoJSON - helps to reduce file size</dd>
    <dt>Export folder</dt>
        <dd>The folder where the webmap will be saved</dd>
    <dt>Mapping library location</dt>
        <dd>Select whether to use a local copy of OL3/Leaflet, or whether to call the library from its CDN</dd>
    <dt>Minify GeoJSON files</dt>
        <dd>Remove unnecessary whitespace from exported GeoJSON to reduce file size</dd>
    <dt>Precision</dt>
        <dd>Reduce geometry accuracy to reduce file size</dd>
</dl>

#### Scale/Zoom
<dl>
    <dt>Extent</dt>
        <dd>Either match the current QGIS view or show all contents of all layers (only local GeoJSON and rasters, not WFS/WMS)</dd>
    <dt>Max zoom level</dt>
        <dd>How far the webmap will zoom in</dd>
    <dt>Min zoom level</dt>
        <dd>How far the webmap will zoom out</dd>
    <dt>Restrict to extent</dt>
        <dd>Prevent panning or zooming beyond the selected extent</dd>
</dl>

#### Appearance
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
        <dd>Create webmap in same projection as QGIS project, otherwise the webmap is projected in EPSG:3857</dd>
    <dt>Show popups on hover</dt>
        <dd>Show popups when mouse hovers over features</dd>
    <dt>Template</dt>
        <dd>Select HTML template for webmap - add your own templates to the /qgis2web/templates directory in your .qgis2 folder</dd>
</dl>

Current limitations
-------------------
* no rule-based rendering
* SVG point markers sometimes do not appear in the preview pane, but work when the map is exported
* Leaflet maps only use each symbol's first symbol layer
* in OL3 maps, only single rendered points cluster, not categorized or graduated
* rasters are exported unstyled
* line style (dashed/dotted) does not appear in OL3 preview, but works in export
* Leaflet can label points, but cannot label lines and polygons
* only a single 2.5d layer will render per map
* 2.5d layers only appear when zoomed in to building scales

Reporting bugs
--------------
Please report any problems you have with qgis2web as we may be unaware that a problem exists. Save time and effort by following these steps:
- Make sure you are using the latest release of qgis2web
- Check the issues on Github to see whether the bug has already been reported, and if so, read through all the comments on the issue, and add any additional information from your experience of the bug
- Make sure you can reproduce the bug reliably
- Reduce the complexity of your bug conditions as far as you can, especially by reducing the number of layers, ideally to one
- Raise a Github issue, including:
  * the qgis2web version (or make it clear if you are using the Github master branch)
  * python error text/stack trace which occurs
  * browser JS console errors - press F12 in qgis2web to open the developer toolbar and find the console
  * screenshot of your settings
  * screenshot of the output
  * a link to the data you used, if possible

The stability of qgis2web relies on your bug reports, so please keep them coming.

Development
-----------
qgis2web is largely developed by Tom Chadwin with significant contributions from a few others. Please, please do contribute, as there is so much more to do.

As for the overall direction of the plugin, there is now basically feature parity between Leaflet and OL3 exports. Any new features should be implemented in both formats, or I am not keen for it to be included.

The core philosophy of the plugin is: don’t get the plugin to do anything which QGIS can already do. Keep the focus on producing good-quality maps, reproducing as much from QGIS as possible, rather than adding additional functionality.

Coding guidelines:
* Comply with <code>PEP8</code>
* Remove <code>print</code> statements before making a pull request
* Run the tests, and don’t break them
* Anything which alters the output for the basic tests will mean updating the control files in <code>/test/data/control</code>
* Write tests for new functionality
* Don't introduce a new client-side library for something which can easily be done without it (I'm looking at you jQuery!)

Other improvements required are:
* Improve code quality/refactor
* Write tests for more functionality - coverage is currently very low

Testing
-------
Commits and pull requests are automatically tested by Travis. The tests are in <code>/test</code>, specifically <code>/test/test_qgis2web_dialog.py</code>. If you want to run these tests locally on Linux, do the following to prepare (assumes Ubuntu or derivative):</p>

Install the pip Python package manager

    apt-get install python-pip

Install nose and coverage which are used to run the tests

    pip install nose
    pip install coverage

Change to the directory which contains the plugin code

    cd ~/.qgis2/python/plugins/qgis2web

Set up the environment specifying the prefix path under which QGIS is installed (commonly /usr or /usr/local).

    source scripts/run-env-linux.sh /usr

Set the QGIS_REPO environment variable to match the QGIS version you are using:

    http://qgis.org/debian-ltr for long term support version
    http://qgis.org/debian for current version
    http://qgis.org/debian-nightly for current master / nightly version

    export QGIS_REPO=http://qgis.org/debian-ltr

Run the tests with:

    make test

### Mac OS X
qgis can be fully installed using homebrew https://github.com/OSGeo/homebrew-osgeo4mac.

There is a shell script to set the qgis paths

    pip install nose
    pip install coverage
    source scripts/run-env-osx-homebrew.sh
    make test

### virtualenv
There may be a problem using virtualenv with pyqgis (or someone might get it working and tell us how). After 'import qgis' there is an error retrieving sip.

### Untested functionality
* rasters
* labels
* rule-based renderer
* SVG markers
* polygon border style "No pen"
* polygon fill style "No brush"
* line cap/join styles
* change export folder via mouse click
* save settings
* click layer popup combo
* unchecked layers initially collapsed and non-visible
* restore saved project/layer settings
* open dev console
* WFS encode to JSON
* close qgis2web
* Leaflet polygon outline: simple line
* Leaflet line style (dot/dash)
* Leaflet line width > 1
* Leaflet categorized clusters
* Leaflet graduated clusters
* Leaflet WMS
* Leaflet WFS clusters
* Leaflet JSON non-point popups
* Leaflet scale-dependent visibility
* Leaflet match CRS
* Leaflet basemaps
* Leaflet basemaps + layers list
* Leaflet cluster + layers list
* Leaflet raster + layers list
* Leaflet project title
* Leaflet highlight + popups on hover
* Leaflet categorized on non-string column
* Leaflet categorized JSON point without popup
* Leaflet custom popup contents via <code>html_prov</code>
* Leaflet export
* OL3 measure - imperial units
* OL3 blank template value
* OL3 layer groups
* OL3 canvas extent
* OL3 WFS cluster
* OL3 layer transparency

If anyone has time to write tests for any of this, it will benefit the plugin hugely. If you do, make sure you delete the tests from this list. Some of the items above I don't even know how to test...</p>

Credits
-------
qgis2web is fundamentally a merge of *Victor Olaya's qgis-ol3* and *Riccardo Klinger's qgis2leaf*. It would not exist without their work. Thank you, gentlemen. Thanks are also very much due to *Paolo Cavallini* who suggested and supported the merge.
* @volaya
* @riccardoklinger
* @pcav

qgis2web could not exist without the monumental software:
* QGIS
* OpenLayers 3
* Leaflet

Thanks are also due for major code contributions to:
* @akbargumbira
* @lucacasagrande
* @walkermatt
* @boesiii

The following libraries have been used:
* ol3-layerswitcher by @walkermatt
* Autolinker.js by @gregjacobs
* requestAnimationFrame polyfill by @paulirish
* Function.prototype.bind polyfill by @mozilla
* Leaflet.draw by @jacobtoye
* Leaflet.label by @jacobtoye
* Leaflet.markercluster by @danzel
* Leaflet.MeasureControl by @makinacorpus
* leaflet-hash by @mlevans
* Proj4js by @madair, @calvinmetcalf, and others
* Proj4Leaflet by @kartena
* OSMBuildings by @kekscom
