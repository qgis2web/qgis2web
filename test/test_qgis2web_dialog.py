# coding=utf-8
"""Dialog test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'riccardo.klinger@geolicious.de'
__date__ = '2015-03-26'
__copyright__ = 'Copyright 2015, Riccardo Klinger / Geolicious'

import unittest

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from PyQt4 import QtCore, QtTest
from PyQt4.QtGui import QDialogButtonBox, QDialog
from utilities import get_qgis_app

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()

from maindialog import MainDialog

class qgis2web_classDialogTest(unittest.TestCase):
    """Test dialog works."""

    def setUp(self):
        """Runs before each test."""
        self.dialog = MainDialog(IFACE)

    def tearDown(self):
        """Runs after each test."""
        self.dialog = None

    def test_OL3(self):
        """Test we can export to OL3."""
        button = self.dialog.buttonUpdateOL
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        # result = self.dialog.result()
        # self.assertEqual(result, QDialog.Accepted)

    def test_Leaflet(self):
        """Test we can export to Leaflet."""
        button = self.dialog.buttonUpdateLeaflet
        QtTest.QTest.mouseClick(button, QtCore.Qt.LeftButton)
        # result = self.dialog.result()
        # self.assertEqual(result, QDialog.Rejected)

if __name__ == "__main__":
    suite = unittest.makeSuite(qgis2web_classDialogTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

