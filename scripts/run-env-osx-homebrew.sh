#!/bin/bash

# Let's use the Homebrew path
QGIS_STUB=/usr/local/opt/qgis-28
if [ -n "$1" ]; then
    QGIS_STUB=$1
fi

export QGIS_PREFIX_PATH=${QGIS_STUB}/QGIS.app/Contents/MacOS
export QGIS_PATH=${QGIS_STUB}/QGIS.app/Contents/MacOS
export LD_LIBRARY_PATH=${QGIS_STUB}/lib:${QGIS_PATH}/lib
export PYTHONPATH=${QGIS_PATH}/../Resources/python:${QGIS_PATH}/../Resources/python/plugins:${PYTHONPATH}

echo "QGIS PATH: $QGIS_PREFIX_PATH"
export QGIS_DEBUG=0
export QGIS_LOG_FILE=/tmp/qgis2web/logs/qgis.log

export PATH=${QGIS_STUB}/bin:${QGIS_PATH}/bin:$PATH

echo "This script is intended to be sourced to set up your shell to"
echo "use QGIS built in $QGIS_PREFIX_PATH"
echo
echo "To use it do:"
echo "source $BASH_SOURCE /your/optional/install/path"
echo
echo "Then use the make file supplied here e.g. make test"
