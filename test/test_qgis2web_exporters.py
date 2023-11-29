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

from twisted.application import internet
from twisted.cred import checkers, portal
from twisted.internet import reactor
from twisted.tap import ftp
from threading import Thread
from twisted.protocols import ftp

# This import is to enable SIP API V2
# noinspection PyUnresolvedReferences
import qgis  # pylint: disable=unused-import

from qgis2web.utils import tempFolder
from qgis2web.exporter import (FolderExporter,
                               FtpExporter,
                               FtpConfigurationDialog,
                               EXPORTER_REGISTRY)
from qgis2web.writer import (WriterResult)

from qgis.testing import start_app

print("test_qgis2web_exporters")
start_app()

TEST_PORT = 3232
FTP_FOLDER = ''
FTP_USER_FOLDER = ''
SERVER_RUNNING = False


def createServer():
    """
    Create a simple (insecure!) ftp server for testing
    """
    global FTP_FOLDER
    global TEST_PORT
    global FTP_USER_FOLDER
    global SERVER_RUNNING

    if SERVER_RUNNING:
        return

    SERVER_RUNNING = True

    FTP_FOLDER = os.path.join(tempFolder(), 'ftp')

    if os.path.exists(FTP_FOLDER):
        shutil.rmtree(FTP_FOLDER)

    os.makedirs(FTP_FOLDER)

    FTP_USER_FOLDER = os.path.join(FTP_FOLDER, 'testuser')
    os.makedirs(FTP_USER_FOLDER)

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

    svc = makeService({'root': FTP_FOLDER, 'userhome': FTP_FOLDER,
                       'userAnonymous': 'anon', 'port': TEST_PORT, 'credCheckers': [c]})
    reactor.callWhenRunning(svc.startService)
    Thread(target=reactor.run, args=(False,)).start()


class qgis2web_exporterTest(unittest.TestCase):

    """Test exporters and exporter registry"""

    def setUp(self):
        """Runs before each test"""
        pass

    @classmethod
    def setUpClass(cls):
        createServer()

    @classmethod
    def tearDownClass(cls):
        """Runs after each test"""
        try:
            reactor.stop()
        except Exception:
            pass

    def test01_FolderExporterDefaultsToTemp(self):
        """Test that folder exporter defaults to a temporary folder"""
        e = FolderExporter()
        self.assertTrue(e.exportDirectory())

    def test02_FolderExporterPostProcess(self):
        """Test folder exporter post processing"""
        e = FolderExporter()
        result = WriterResult()
        result.index_file = '/tmp/file.htm'
        e.postProcess(result)
        self.assertEqual(e.destinationUrl(), '/tmp/file.htm')

    def test03_FolderExporterSaveReadFromProject(self):
        """Test saving and restoring folder exporter settings in project"""
        e = FolderExporter()
        e.folder = '/my_folder'
        e.writeToProject()

        restored = FolderExporter()
        restored.readFromProject()

        self.assertEqual(restored.exportDirectory(), '/my_folder')

    def test04_RegistryHasExporters(self):
        """test that exporter registry is populated with exporters"""
        self.assertTrue(FolderExporter in EXPORTER_REGISTRY.getExporters())

    def test05_RegistrySaveReadFromProject(self):
        """ test saving and restoring current exporter in project"""
        e = FolderExporter()
        e.folder = '/my_folder'
        EXPORTER_REGISTRY.writeToProject(e)

        restored = EXPORTER_REGISTRY.createFromProject()
        self.assertEqual(type(restored), FolderExporter)
        self.assertEqual(restored.exportDirectory(), '/my_folder')

        # try with a non-folder exporter
        f = FtpExporter()
        EXPORTER_REGISTRY.writeToProject(f)
        restored = EXPORTER_REGISTRY.createFromProject()
        self.assertEqual(type(restored), FtpExporter)

    def test06_FtpConfigurationDialog(self):
        """Test behavior of the FTP export configuration dialog"""
        dlg = FtpConfigurationDialog()
        # should default to port 21
        self.assertEqual(dlg.port(), 21)
        # test getters and setters
        dlg.setHost('myhost')
        self.assertEqual(dlg.host(), 'myhost')
        dlg.setUsername('super')
        self.assertEqual(dlg.username(), 'super')
        dlg.setPort(54)
        self.assertEqual(dlg.port(), 54)
        dlg.setFolder('folder')
        self.assertEqual(dlg.folder(), 'folder')

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

        self.assertEqual(restored.host, 'geocities.com')
        self.assertEqual(restored.username, 'sup3Raw3s0m64')
        self.assertEqual(restored.remote_folder, 'test_folder')
        self.assertEqual(restored.port, 123)

    def test08_FtpExporterTempFolder(self):
        """Test FTP exporter generation of temp folder"""
        e = FtpExporter()
        e.host = None
        self.assertTrue(e.exportDirectory())
        prev_folder = e.exportDirectory()

        result = WriterResult()
        result.index_file = ''
        e.postProcess(result)
        # a new export folder should be generated to avoid outdated files
        self.assertNotEqual(e.exportDirectory(), prev_folder)

    def test09_FtpUpload(self):
        e = FtpExporter()
        e.host = 'localhost'
        e.port = TEST_PORT
        e.username = 'testuser'
        e.password = 'pw'

        # copy some files to export directory
        export_folder = e.exportDirectory()
        try:
            os.makedirs(export_folder)
        except Exception:
            self.assertTrue(False, 'could not create export directory')
        out_file = os.path.join(export_folder, 'index.html')
        with open(out_file, 'w') as i:
            i.write('test')

        result = WriterResult()
        result.index_file = out_file
        result.folder = export_folder
        e.postProcess(result)

        expected_index_file = os.path.join(
            FTP_USER_FOLDER, 'public_html', 'index.html')
        self.assertTrue(os.path.exists(expected_index_file))
        f = open(expected_index_file, 'r')
        content = f.readlines()
        f.close()
        self.assertEqual(content, ['test'])

        # try overwriting existing file
        with open(out_file, 'w') as i:
            i.write('test2')
        result = WriterResult()
        result.index_file = out_file
        result.folder = export_folder
        e.postProcess(result)
        self.assertTrue(expected_index_file)
        f = open(expected_index_file, 'r')
        content = f.readlines()
        f.close()
        self.assertEqual(content, ['test2'])

    def test10_FtpUploadSubfolder(self):
        e = FtpExporter()
        e.host = 'localhost'
        e.port = TEST_PORT
        e.username = 'testuser'
        e.password = 'pw'

        # copy some files to export directory
        export_folder = e.exportDirectory()
        try:
            os.makedirs(export_folder)
        except Exception:
            self.assertTrue(False, 'could not create export directory')
        out_file = os.path.join(export_folder, 'index.html')
        with open(out_file, 'w') as i:
            i.write('test')
        sub_folder = os.path.join(export_folder, 'sub')
        try:
            os.makedirs(sub_folder)
        except Exception:
            self.assertTrue(False, 'could not create export directory')
        sub_folder_out_file = os.path.join(sub_folder, 'index.html')
        with open(sub_folder_out_file, 'w') as i:
            i.write('test2')

        result = WriterResult()
        result.index_file = out_file
        result.folder = export_folder
        e.postProcess(result)

        expected_index_file = os.path.join(
            FTP_USER_FOLDER, 'public_html', 'index.html')
        self.assertTrue(os.path.exists(expected_index_file))
        f = open(expected_index_file, 'r')
        content = f.readlines()
        f.close()
        self.assertEqual(content, ['test'])
        expected_sub_folder_index_file = os.path.join(
            FTP_USER_FOLDER, 'public_html', 'sub', 'index.html')
        self.assertTrue(os.path.exists(expected_sub_folder_index_file))
        f = open(expected_sub_folder_index_file, 'r')
        content = f.readlines()
        f.close()
        self.assertEqual(content, ['test2'])


if __name__ == "__main__":
    suite = unittest.TestSuite()
    suite.addTests(unittest.makeSuite(qgis2web_exporterTest))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
