<h1>Contributing to qgis2web</h1>

<h2>Development</h2>
<p>qgis2web is largely developed by me, with significant contributions from a
few others. Please, please do contribute, as there is so much more to do.</p>

<p>As for the overall direction of the plugin, there is now basically feature
parity between Leaflet and OL3 exports. Any new features should be implemented
in both formats, or I am not keen for it to be included.</p>

<p>The core philosophy of the plugin is: don’t get the plugin to do anything
which QGIS can already do. Also, keep focused on producing good-quality maps,
reproducing as much from QGIS as possible, rather than adding extra new
functionality.</p>

<p>Coding guidelines:</p>
<ul>
    <li>Comply with PEP8</li>
    <li>Remove <code>print</code> statements before making a pull request</li>
    <li>Don’t break the tests themselves (all in test/test_qgis2web_dialog.py)
    </li>
    <li>Anything which alters the output for the basic tests will mean updating
    the control files in /test/data/control</li>
    <li>Write tests for new functionality</li>
    <li>Don't introduce a new client-side library for something which can
    easily be done without it (I'm looking at you, jQuery)</li>
</ul>

<p>Other improvements required are:</p>
<ul>
    <li>Improve code quality/refactor</li>
    <li>Write tests for more functionality - coverage is currently very low
    </li>
</ul>

<h2>Testing</h2>

<p>All commits and PRs are tested by Travis. The tests are in <code>/test
</code>, specifically <code>/test/test_qgis2web_dialog.py</code>. If you want
to run these tests locally on Linux, do the following to prepare (assumes
Ubuntu or derivative):</p>

<pre><code># Install the pip Python package manager

apt-get install python-pip

# Using pip install nose which is used to run the tests

pip install nose

# Change to the directory which contains the plugin code

cd ~/.qgis2/python/plugins/qgis2web

# Set up the enviroment specifying the prefix path under which QGIS is
# installed (commonly /usr or /usr/local).

source scripts/run-env-linux.sh /usr

# Set the QGIS_REPO environent variable to match the QGIS version you are
# using:
# http://qgis.org/debian-ltr for long term support version
# http://qgis.org/debian for current version
# http://qgis.org/debian-nightly for current master / nightly version

export QGIS_REPO=http://qgis.org/debian-ltr
</code></pre>
<p>Run the tests with:</p>
<pre><code>make test</code></pre>

<p>Untested functionality includes:</p>
<ul>
    <li>labels</li>
    <li>rule-based renderer</li>
    <li>SVG markers</li>
    <li>heatmaps</li>
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

<p>If anyone has time to write tests for any of this, it will benefit the
plugin hugely. If you do, make sure you delete the tests from this list. Some
of the items above I don't even know how to test...</p>
