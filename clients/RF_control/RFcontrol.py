from common.lib.clients.qtui.QCustomFreqPower import QCustomFreqPower
from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import Connection

from PyQt5.QtWidgets import *
import logging

logger = logging.getLogger(__name__)


class RFcontrol(QWidget):

    def __init__(self, reactor, cxn=None):
        super(RFcontrol, self).__init__()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        self.reactor = reactor
        self.cxn = cxn
        import labrad.types
        self.types = labrad.types
        self.chan = 'RF_Drive'
        self.connect()

    @inlineCallbacks
    def connect(self):
        """
        Creates an Asynchronous connection to Pulser and
        connects incoming signals to relavent functions
        """

        if self.cxn is None:
            self.cxn = Connection(name="RF Control")
            yield self.cxn.connect()
        self.server = yield self.cxn.get_server('Pulser')
        self.initialize_gui()

    @inlineCallbacks
    def initialize_gui(self):
        layout = QGridLayout()
        chans = yield self.server.get_dds_channels()
        if self.chan in chans:
            self.freq_power_widget = QCustomFreqPower(title='Trap RF Control')
            min_power, max_power = yield self.server.get_dds_amplitude_range(self.chan)
            min_freq, max_freq = yield self.server.get_dds_frequency_range(self.chan)
            self.freq_power_widget.set_power_range((min_power, max_power))
            self.freq_power_widget.set_freq_range((min_freq, max_freq))
            initpower = yield self.server.amplitude(self.chan)
            initfreq = yield self.server.frequency(self.chan)
            initstate = yield self.server.output(self.chan)
            self.freq_power_widget.freq_spinbox.setSingleStep(0.001)
            self.freq_power_widget.set_state_no_signal(initstate)
            self.freq_power_widget.set_power_no_signal(initpower['dBm'])
            self.freq_power_widget.set_freq_no_signal(initfreq['MHz'])
            self.freq_power_widget.power_spinbox.valueChanged.connect(self.power_changed)
            self.freq_power_widget.freq_spinbox.valueChanged.connect(self.freq_changed)
            self.freq_power_widget.switch_button.toggled.connect(self.switch_changed)
            layout.addWidget(self.freq_power_widget)

        self.setLayout(layout)

    @inlineCallbacks
    def power_changed(self, pwr):
        val = self.types.Value(pwr, 'dBm')
        try:
            yield self.server.amplitude(self.chan, val)
        except self.types.Error as e:
            old_value = yield self.server.amplitude(self.chan)
            self.freq_power_widget.set_power_no_signal(old_value)
            self.display_error(e.msg)

    @inlineCallbacks
    def freq_changed(self, freq):
        val = self.types.Value(freq, 'MHz')
        try:
            yield self.server.frequency(self.chan, val)
        except self.types.Error as e:
            old_value = yield self.server.frequency(self.chan)
            self.freq_power_widget.set_freq_no_signal(old_value)
            self.display_error(e.msg)

    @inlineCallbacks
    def switch_changed(self, pressed):
        try:
            yield self.server.output(self.chan, pressed)
        except self.types.Error as e:
            old_value = yield self.server.frequency(self.chan)
            self.freq_power_widget.set_state_no_signal(old_value)
            self.display_error(e.msg)

    def display_error(self, text):
        # runs the message box in a non-blocking method
        message = QMessageBox(self)
        message.setText(text)
        message.open()
        message.show()
        message.raise_()

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QApplication([])
    import qt5reactor

    qt5reactor.install()
    from twisted.internet import reactor

    RFcontrolWidget = RFcontrol(reactor)
    RFcontrolWidget.show()
    reactor.run()
