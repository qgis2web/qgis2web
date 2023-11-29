# coding=utf-8
"""Resources test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'riccardo.klinger@geolicious.de'
__date__ = '2015-03-26'
__copyright__ = 'Copyright 2015, Riccardo Klinger / Geolicious'

from PyQt5.QtGui import QIcon
from qgis.testing import unittest, start_app

print("test_resources.py")
start_app()


class qgis2web_classDialogTest(unittest.TestCase):
    """Test rerources work."""

    def setUp(self):
        """Runs before each test."""
        pass

    def tearDown(self):
        """Runs after each test."""
        pass

    def test_icon_png(self):
        """Read icon from resources"""
        path = ':/plugins/qgis2web_class/icon.png'
        icon = QIcon(path)
        self.assertFalse(icon.isNull())

if __name__ == "__main__":
    suite = unittest.makeSuite(qgis2web_classResourcesTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)



