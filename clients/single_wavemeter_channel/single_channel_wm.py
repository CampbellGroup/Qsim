#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue
import socket
import os

SIGNALID1 = 445567


class single_channel_wm(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(single_channel_wm, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the wavemeter computer and
        connects incoming signals to relavent functions
        """
        from labrad.wrappers import connectAsync
        self.password = os.environ['LABRADPASSWORD']
        self.cxn = yield connectAsync('10.97.112.4', name = socket.gethostname() + ' Single Channel Lock', password=self.password)
        self.server = yield self.cxn.multiplexerserver
        yield self.server.signal__frequency_changed(SIGNALID1)
        yield self.server.addListener(listener = self.updateFrequency, source = None, ID = SIGNALID1)

        self.initializeGUI()

    def initializeGUI(self):

        layout = QtGui.QGridLayout()
        qBox = QtGui.QGroupBox('WS7')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0), returnValue
        self.centralwidget = QtGui.QWidget(self)
        self.wavelength = QtGui.QLabel('freq')
        self.wavelength.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=70))
        self.wavelength.setAlignment(QtCore.Qt.AlignCenter)
        self.wavelength.setStyleSheet('color: blue')
        subLayout.addWidget(self.wavelength, 1,0)

        self.setLayout(layout)

    def updateFrequency(self, c, signal):
        if signal[0] == 1:
            self.wavelength.setText(str(signal[1])[0:10])

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    single_chan_Widget = single_channel_wm(reactor)
    single_chan_Widget.show()
    reactor.run()
