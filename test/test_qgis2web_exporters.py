# -*- coding: utf-8 -*-

# Copyright (C) 2017 Nyall Dawson (nyall.dawson@gmail.com)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

__author__ = 'nyall.dawson@gmail.com'
__date__ = '2017-02-15'
__copyright__ = 'Copyright 2017, Nyall Dawson'

import unittest
import os
import shutil
import difflib

from twisted.application import internet
from twisted.cred import checkers, portal
from twisted.internet import reactor
from twisted.tap import ftp
from threading import Thread
from twisted.protocols import ftp

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import
from qgis.core import QgsProject
from qgis.core import QgsVectorLayer, QgsMapLayerRegistry, QgsCoordinateReferenceSystem
from PyQt4 import QtCore, QtTest

from utils import tempFolder
from utilities import get_qgis_app, test_data_path, load_layer, load_wfs_layer
from exporter import (FolderExporter,
                      FtpExporter,
                      FtpConfigurationDialog,
                      EXPORTER_REGISTRY)

QGIS_APP, CANVAS, IFACE, PARENT = get_qgis_app()


class qgis2web_exporterTest(unittest.TestCase):
    """Test exporters and exporter registry"""

    def setUp(self):
        """Runs before each test"""
        self.test_port = 3232

    def tearDown(self):
        """Runs after each test"""
        try:
            self.stopServer()
        except:
            pass

    def createServer(self):
        """
        Create a simple (insecure!) ftp server for testing
        """
        self.ftp_folder = os.path.join(tempFolder(),'ftp')

        if os.path.exists(self.ftp_folder):
            shutil.rmtree(self.ftp_folder)

        os.makedirs(self.ftp_folder)

        self.user_ftp_folder = os.path.join(self.ftp_folder,'testuser')
        os.makedirs(self.user_ftp_folder)

        c = checkers.InMemoryUsernamePasswordDatabaseDontUse()
        c.addUser('testuser', 'pw')

        def makeService(config):
            f = ftp.FTPFactory()

            r = ftp.FTPRealm(config['root'], userHome=config['userhome'])
            p = portal.Portal(r, config.get('credCheckers', []))

            f.tld = config['root']
            f.userAnonymous = config['userAnonymous']
            f.portal = p
            f.protocol = ftp.FTP

            try:
                portno = int(config['port'])
            except KeyError:
                portno = 2121
            return internet.TCPServer(portno, f)

        svc=makeService({'root':self.ftp_folder,'userhome':self.ftp_folder,
                         'userAnonymous': 'anon', 'port':self.test_port,'credCheckers':[c]})
        reactor.callWhenRunning(svc.startService)
        Thread(target=reactor.run, args=(False,)).start()

    def stopServer(self):
        """
        Shutdown the running server
        """
        reactor.stop()

    def test01_FolderExporterDefaultsToTemp(self):
        """Test that folder exporter defaults to a temporary folder"""
        e = FolderExporter()
        self.assertTrue(e.exportDirectory())

    def test02_FolderExporterPostProcess(self):
        """Test folder exporter post processing"""
        e = FolderExporter()
        e.postProcess('/tmp/file.htm')
        self.assertEqual(e.destinationUrl(),'/tmp/file.htm')

    def test03_FolderExporterSaveReadFromProject(self):
        """Test saving and restoring folder exporter settings in project"""
        e = FolderExporter()
        e.folder = '/my_folder'
        e.writeToProject()

        restored = FolderExporter()
        restored.readFromProject()

        self.assertEqual(restored.exportDirectory(),'/my_folder')

    def test04_RegistryHasExporters(self):
        """test that exporter registry is populated with exporters"""
        self.assertTrue(FolderExporter in EXPORTER_REGISTRY.getExporters())

    def test05_RegistrySaveReadFromProject(self):
        """ test saving and restoring current exporter in project"""
        e = FolderExporter()
        e.folder = '/my_folder'
        EXPORTER_REGISTRY.writeToProject(e)

        restored = EXPORTER_REGISTRY.createFromProject()
        self.assertEqual(type(restored),FolderExporter)
        self.assertEqual(restored.exportDirectory(), '/my_folder')

        # try with a non-folder exporter
        f = FtpExporter()
        EXPORTER_REGISTRY.writeToProject(f)
        restored = EXPORTER_REGISTRY.createFromProject()
        self.assertEqual(type(restored),FtpExporter)

    def test06_FtpConfigurationDialog(self):
        """Test behavior of the FTP export configuration dialog"""
        dlg = FtpConfigurationDialog()
        # should default to port 21
        self.assertEqual(dlg.port(),21)
        # test getters and setters
        dlg.setHost('myhost')
        self.assertEqual(dlg.host(),'myhost')
        dlg.setUsername('super')
        self.assertEqual(dlg.username(),'super')
        dlg.setPort(54)
        self.assertEqual(dlg.port(),54)
        dlg.setFolder('folder')
        self.assertEqual(dlg.folder(),'folder')

        # try setting port to a non-int
        dlg.setPort('a')
        self.assertEqual(dlg.port(), 54)

    def test07_FtpExporterSaveReadFromProject(self):
        """Test saving and restoring FTP exporter settings in project"""
        e = FtpExporter()
        e.host = 'geocities.com'
        e.username = 'sup3Raw3s0m64'
        e.port = 123
        e.remote_folder = 'test_folder'
        e.writeToProject()

        restored = FtpExporter()
        restored.readFromProject()

        self.assertEqual(restored.host,'geocities.com')
        self.assertEqual(restored.username,'sup3Raw3s0m64')
        self.assertEqual(restored.remote_folder,'test_folder')
        self.assertEqual(restored.port,123)

    def test08_FtpExporterTempFolder(self):
        """Test FTP exporter generation of temp folder"""
        e = FtpExporter()
        e.host = None
        self.assertTrue(e.exportDirectory())
        prev_folder = e.exportDirectory()

        e.postProcess('')
        # a new export folder should be generated to avoid outdated files
        self.assertNotEqual(e.exportDirectory(), prev_folder)

    def test09_FtpUpload(self):
        self.createServer()

        e = FtpExporter()
        e.host = 'localhost'
        e.port = self.test_port
        e.username = 'testuser'
        e.password = 'pw'

        # copy some files to export directory
        export_folder = e.exportDirectory()
        try:
            os.makedirs(export_folder)
        except:
            self.assertTrue(False, 'could not create export directory')
        out_file = os.path.join(export_folder,'index.html')
        with open(out_file,'w') as i:
            i.write('test')

        e.postProcess(out_file)

        expected_index_file = os.path.join(self.user_ftp_folder,'public_html','index.html')
        self.assertTrue(os.path.exists(expected_index_file))
        content = open(expected_index_file,'r').readlines()
        self.assertEqual(content,['test'])

        # try overwriting existing file
        with open(out_file,'w') as i:
            i.write('test2')
        e.postProcess(out_file)
        self.assertTrue(os.path.exists(os.path.join(self.user_ftp_folder,'public_html','index.html')))
        content = open(expected_index_file,'r').readlines()
        self.assertEqual(content,['test2'])




if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(qgis2web_exporterTest))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
