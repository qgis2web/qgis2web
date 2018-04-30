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
apt-get -y install python3-pip
python3 -m pip install --upgrade pip
python3 -m pip install coverage
python3 -m pip install nose
python3 -m pip install rednose
python3 -m pip install --upgrade pycodestyle
apt remove pylint
python3 -m pip install pylint
python3 -m pip install python-coveralls
python3 -m pip install Twisted
python3 -m pip install future

export PYTHONPATH=/usr/share/qgis/python/plugins:$PYTHONPATH

pycodestyle --exclude=test,resources*.py,exp2js.py,ui*.py,xmltodict.py ./ --format=pylint --ignore=E722,W504
# pylint qgis2web.py
QGIS_DEBUG=0 xvfb-run --server-args="-screen 0, 1024x768x24" nosetests -s --nologcapture -A 'not slow' -v --rednose --with-coverage --verbose --cover-package=qgis2web --cover-package=maindialog --cover-package=utils --cover-package=configparams --cover-package=olwriter --cover-package=leafletWriter  --cover-package=olScriptStrings --cover-package=olFileScripts --cover-package=olStyleScripts --cover-package=olLayerScripts --cover-package=basemaps --cover-package=leafletFileScripts --cover-package=leafletLayerScripts --cover-package=leafletScriptStrings --cover-package=leafletStyleScripts --cover-package=exporter --cover-package=writerRegistry --cover-package=writer
popd
