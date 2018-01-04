ARG QGIS_TEST_VERSION=latest
FROM  qgis/qgis:${QGIS_TEST_VERSION}
MAINTAINER Matthias Kuhn <matthias@opengis.ch>

RUN apt-get update && \
    apt-get -y install python3-pyqt5.qtwebkit python-pyqt5.qtwebkitwidgets

ENV LANG=C.UTF-8

WORKDIR /
