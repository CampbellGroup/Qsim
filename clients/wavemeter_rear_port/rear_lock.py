from common.lib.clients.qtui.switch import QCustomSwitchChannel
from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
import os
import socket
from PyQt4 import QtGui


class cal_lock(QtGui.QWidget):

    def __init__(self, reactor):
        super(cal_lock, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.set = 811.291420
        self.gain = 1500.0
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions

        """

        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync()
        self.server = self.cxn.single_wm_lock_server
        self.initializeGUI()

    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        lockwidget = QCustomSwitchChannel('Lock Cal', ('Locked', 'Unlocked'))
        lockwidget.TTLswitch.toggled.connect(self.toggle)

        offsetwidget = QCustomSpinBox('DC offset', (-1.0, 1.0))
        setpointwidget = QCustomSpinBox('Set Point', (811.0, 812.0))
        gainwidget = QCustomSpinBox('Gain', (0.1, 10000.0))

        offsetwidget.setStepSize(0.001)
        setpointwidget.setStepSize(0.000001)
        gainwidget.setStepSize(0.1)

        offsetwidget.spinLevel.setDecimals(3)
        setpointwidget.spinLevel.setDecimals(6)
        gainwidget.spinLevel.setDecimals(1)

        setpointwidget.spinLevel.setValue(self.set)
        gainwidget.spinLevel.setValue(self.gain)

        offsetwidget.spinLevel.valueChanged.connect(self.offset)
        setpointwidget.spinLevel.valueChanged.connect(self.set_point)
        gainwidget.spinLevel.valueChanged.connect(self.set_gain)

        layout.addWidget(lockwidget, 0, 0)
        layout.addWidget(offsetwidget, 0, 1)
        layout.addWidget(setpointwidget, 0, 2)
        layout.addWidget(gainwidget, 0, 3)

        self.setLayout(layout)

    @inlineCallbacks
    def toggle(self, state):
        yield self.server.toggle(state)

    @inlineCallbacks
    def offset(self, offset):
        yield self.server.offset(offset)

    @inlineCallbacks
    def set_point(self, set_point):
        yield self.server.set_point(set_point)

    @inlineCallbacks
    def set_gain(self, gain):
        yield self.server.set_gain(gain)

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    cal_lock_Widget = cal_lock(reactor)
    cal_lock_Widget.show()
    reactor.run()