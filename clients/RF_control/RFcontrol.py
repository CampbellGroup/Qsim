from common.lib.clients.qtui.QCustomFreqPower import QCustomFreqPower
from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui


class RFcontrol(QtGui.QWidget):

    def __init__(self, reactor, cxn=None):
        super(RFcontrol, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.cxn = cxn
        from labrad import types as T
        from labrad.types import Error
        self.Error = Error
        self.T = T
        self.chan = 'RF_Drive'
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to Pulser and
        connects incoming signals to relavent functions

        """

        if self.cxn is None:
            self.cxn = connection(name="RF Control")
            yield self.cxn.connect()
        self.server = yield self.cxn.get_server('Pulser')
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        chans = yield self.server.get_dds_channels()
        if self.chan in chans:
            widget = QCustomFreqPower(self.chan)
            MinPower, MaxPower = yield self.server.get_dds_amplitude_range(self.chan)
            MinFreq, MaxFreq = yield self.server.get_dds_frequency_range(self.chan)
            widget.setPowerRange((MinPower, MaxPower))
            widget.setFreqRange((MinFreq, MaxFreq))
            initpower = yield self.server.amplitude(self.chan)
            initfreq = yield self.server.frequency(self.chan)
            initstate = yield self.server.output(self.chan)
            widget.spinFreq.setSingleStep(0.001)
            widget.setStateNoSignal(initstate)
            widget.setPowerNoSignal(initpower['dBm'])
            widget.setFreqNoSignal(initfreq['MHz'])
            widget.spinPower.valueChanged.connect(self.powerChanged)
            widget.spinFreq.valueChanged.connect(self.freqChanged) 
            widget.buttonSwitch.toggled.connect(self.switchChanged)
            layout.addWidget(widget)

        self.setLayout(layout)

    @inlineCallbacks
    def powerChanged(self, pwr):
        val = self.T.Value(pwr, 'dBm')
        try:
            yield self.server.amplitude(self.chan, val)
        except self.Error as e:
            old_value = yield self.server.amplitude(self.chan)
            self.setPowerNoSignal(old_value)
            self.displayError(e.msg)

    @inlineCallbacks
    def freqChanged(self, freq):
        val = self.T.Value(freq, 'MHz')
        try:
            yield self.server.frequency(self.chan, val)
        except self.Error as e:
            old_value = yield self.server.frequency(self.chan)
            self.setFreqNoSignal(old_value)
            self.displayError(e.msg)

    @inlineCallbacks
    def switchChanged(self, pressed):
        try:
            yield self.server.output(self.chan, pressed)
        except self.Error as e:
            old_value = yield self.server.frequency(self.chan)
            self.setStateNoSignal(old_value)
            self.displayError(e.msg)

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    RFcontrolWidget = RFcontrol(reactor)
    RFcontrolWidget.show()
    reactor.run()
