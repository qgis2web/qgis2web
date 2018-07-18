# coding=utf-8
"""Safe Translations Test.

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
from utilities import get_qgis_app

__author__ = 'ismailsunni@yahoo.co.id'
__date__ = '12/10/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')
import unittest
import os

from PyQt4.QtCore import QCoreApplication, QTranslator

QGIS_APP = get_qgis_app()


class SafeTranslationsTest(unittest.TestCase):
    """Test translations work."""

    def setUp(self):
        """Runs before each test."""
        if 'LANG' in os.environ.iterkeys():
            os.environ.__delitem__('LANG')

    def tearDown(self):
        """Runs after each test."""
        if 'LANG' in os.environ.iterkeys():
            os.environ.__delitem__('LANG')

    def test_qgis_translations(self):
        """Test that translations work."""
        parent_path = os.path.join(__file__, os.path.pardir, os.path.pardir)
        dir_path = os.path.abspath(parent_path)
        file_path = os.path.join(
            dir_path, 'i18n', 'af.qm')
        translator = QTranslator()
        translator.load(file_path)
        QCoreApplication.installTranslator(translator)

        expected_message = 'Goeie more'
        real_message = QCoreApplication.translate("@default", 'Good morning')
        self.assertEqual(real_message, expected_message)


if __name__ == "__main__":
    suite = unittest.makeSuite(SafeTranslationsTest)
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
