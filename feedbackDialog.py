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

from qgis.PyQt.QtCore import QObject, QCoreApplication
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox
from .ui_feedback_dialog import Ui_Feedback

translator = QObject()


class Feedback(object):

    """
    Interface for feedback objects. Can itself be used to provide 'silent'
    feedback (not shown or logged anywhere)
    """

    def cancelled(self):
        """
        Returns True if user has requested cancelation
        """
        return False

    def acceptCancel(self):
        """
        Should be called when an object has detected that
        the feedback has been cancelled and has aborted its
        processing
        """
        pass

    def reset(self):
        """
        Resets the feedback object
        """
        pass

    def completeStep(self):
        """
        Sets the previous message to completed
        """
        pass

    def setCompleted(self, text):
        """
        Sets the feedback to a "completed" message
        """
        pass

    def showFeedback(self, feedback):
        """
        Shows a feedback message
        """
        pass

    def setFatalError(self, error):
        """
        Shows a fatal error message
        """
        pass

    def setProgress(self, progress):
        """
        Sets the progress (in %) for the progress bar
        """
        pass


class FeedbackDialog(QDialog, Ui_Feedback, Feedback):

    """
    A dialog for showing feedback
    """

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.is_cancelled = False
        self.messages = []
        self.buttonBox.button(
            QDialogButtonBox.Cancel).clicked.connect(self.cancel)
        self.progressBar.setRange(0, 0)

    def processEvents(self):
        # hack copied from QgsVectorLayerInterruption.... .mustStop
        # to allow responsive cancelation on linux
        i = 0
        while i < 100 and QCoreApplication.hasPendingEvents():
            QCoreApplication.processEvents()
            i += 1

    def cancel(self):
        self.is_cancelled = True

    def cancelled(self):
        self.processEvents()
        return self.is_cancelled

    def acceptCancel(self):
        self.setFatalError('User cancelled')

    def reset(self):
        self.is_cancelled = False
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(True)
        self.messages = []
        self.progressBar.setRange(0, 0)

    def pushHtml(self, html):
        self.messages.append(html)
        self.feedbackText.document().setHtml('<br/>'.join(self.messages))
        self.processEvents()
        scrollbar = self.feedbackText.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        self.processEvents()

    def showFeedback(self, feedback):
        self.pushHtml(feedback)

    def completeStep(self):
        self.messages[-1] = self.messages[-1] + """
            <span style="color: green">done</span>"""
        self.feedbackText.document().setHtml('<br/>'.join(self.messages))
        self.processEvents()
        scrollbar = self.feedbackText.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        self.processEvents()

    def setFatalError(self, error):
        self.progressBar.setRange(0, 100)
        self.pushHtml('<span style="color:red">{}</span>'.format(error))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)

    def setCompleted(self, feedback):
        self.setProgress(100)
        self.pushHtml('<span style="color: green">{}</span>'.format(feedback))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(True)
        self.buttonBox.button(QDialogButtonBox.Cancel).setEnabled(False)

    def setProgress(self, progress):
        if not self.progressBar.maximum() == 100:
            self.progressBar.setRange(0, 100)
        self.progressBar.setValue(progress)
        self.processEvents()
