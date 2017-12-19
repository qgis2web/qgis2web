#!/usr/bin/env bash
#***************************************************************************
#                             -------------------
#       begin                : 2017-08-24
#       git sha              : :%H$
#       copyright            : (C) 2017 by OPENGIS.ch
#       email                : info@opengis.ch
#***************************************************************************
#
#***************************************************************************
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 2 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#***************************************************************************

set -e

pushd /usr/src
apt-get install python-software-properties
pip install --upgrade pip
pip install coverage
pip install nose
pip install rednose
pip install --upgrade pycodestyle
apt-get install pylint
pip install python-coveralls

pycodestyle --exclude=test,resources*.py,exp2js.py,ui*.py,xmltodict.py ./ --format=pylint --ignore=E722
make pylint
QGIS_DEBUG=0 xvfb-run --server-args="-screen 0, 1024x768x24" nosetests -s --nologcapture -A 'not slow' -v --rednose --with-coverage --verbose --cover-package=qgis2web --cover-package=maindialog --cover-package=utils --cover-package=configparams --cover-package=olwriter --cover-package=leafletWriter  --cover-package=olScriptStrings --cover-package=olFileScripts --cover-package=olStyleScripts --cover-package=olLayerScripts --cover-package=basemaps --cover-package=leafletFileScripts --cover-package=leafletLayerScripts --cover-package=leafletScriptStrings --cover-package=leafletStyleScripts --cover-package=exporter --cover-package=writerRegistry --cover-package=writer
popd
