from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from clients.dac_control.electrode_widget import ElectrodeIndicator
from twisted.internet.defer import inlineCallbacks
from PyQt5.QtWidgets import *
from config.dac_ad660_config import HardwareConfiguration as HC
from config.dac_ad660_config import MultipoleConfiguration as MC
import logging
import time

logger = logging.getLogger(__name__)


class DACClient(QFrame):

    def __init__(self, reactor, parent=None):
        super(DACClient, self).__init__()
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.reactor = reactor
        self.connect()

    @inlineCallbacks
    def connect(self):

        from labrad.wrappers import connectAsync
        self.dac_channels = HC.dac_channels

        self.cxn = yield connectAsync(name="dac client")
        self.multipole_server = self.cxn.multipole_server
        self.dacserver = self.cxn.dac_ad660_server

        self.init_voltages = yield self.dacserver.get_current_voltages()
        self.init_voltages = dict(self.init_voltages)
        self.init_multipoles = yield self.multipole_server.get_multipoles()

        logger.info(f"init voltages:   {list(self.init_voltages.values())}")
        logger.info(f"init multipoles: {self.init_multipoles}")
        self.initialize_gui()

    def initialize_gui(self):
        layout = QVBoxLayout()

        # Make the grid of DAC input spinboxes

        dac_box = QGroupBox('DAC Channels')
        dac_layout = QGridLayout()
        dac_box.setLayout(dac_layout)

        self.electrode_spinboxes = []
        length_of_column = 2
        for i, channel in enumerate(self.dac_channels):
            spinbox = QCustomSpinBox(channel.name,
                                     (channel.allowed_voltage_range[0], channel.allowed_voltage_range[1]))
            spinbox.spinLevel.setValue(0.0)
            spinbox.setStepSize(0.0001)
            spinbox.spinLevel.setDecimals(4)
            spinbox.spinLevel.setValue(self.init_voltages[channel.dac_channel_number])
            spinbox.spinLevel.valueChanged.connect(lambda val=spinbox.spinLevel.value(),
                                                          chan=channel: self.update_dac(val, chan))
            if channel.displayed:
                dac_layout.addWidget(spinbox, i % length_of_column, i // length_of_column)
            self.electrode_spinboxes.append(spinbox)

        # Build the grid of multipole input spinboxes

        multipole_box = QGroupBox('Multipoles')
        multipole_layout = QGridLayout()
        multipole_box.setLayout(multipole_layout)

        self.multipole_spinboxes = []
        length_of_column = 2
        for i, multipole in enumerate(MC.multipoles):
            spinbox = QCustomSpinBox(multipole.name, (-100, 100))
            spinbox.setStepSize(0.001)
            spinbox.spinLevel.setDecimals(3)
            spinbox.spinLevel.setValue(self.init_multipoles[i])
            spinbox.spinLevel.valueChanged.connect(self.change_multipole)
            if multipole.displayed:
                multipole_layout.addWidget(spinbox, i % length_of_column, i // length_of_column)
            self.multipole_spinboxes.append(spinbox)

        self.electrode_indicator = ElectrodeIndicator()
        for port, v in self.init_voltages.items():
            self.electrode_indicator.update_rod(port, v)

        layout.addWidget(self.electrode_indicator)
        layout.addWidget(dac_box)
        layout.addWidget(multipole_box)
        self.setLayout(layout)
        self.maximumSize()

    @inlineCallbacks
    def update_dac(self, voltage, channel):
        dac = channel.dac_channel_number
        yield self.dacserver.set_individual_analog_voltages([(dac, voltage)])
        self.electrode_indicator.update_rod(dac, voltage)

    @inlineCallbacks
    def change_multipole(self, value):
        self.start = time.time()
        mvector = []
        for multipole in self.multipole_spinboxes:
            mvector.append(multipole.spinLevel.value())
        evector = yield self.multipole_server.set_multipoles(mvector)
        if len(evector) == 8:
            for i, voltage in enumerate(evector):
                electrode = self.electrode_spinboxes[i]
                dac_channel = self.dac_channels[i]
                electrode.spinLevel.setValue(voltage)
                self.electrode_indicator.update_rod(dac_channel.dac_channel_number, voltage)

    def closeEvent(self, event):
        pass


if __name__ == "__main__":
    a = QApplication([])
    import qt5reactor

    qt5reactor.install()
    from twisted.internet import reactor

    dacWidget = DACClient(reactor)
    dacWidget.show()
    # noinspection PyUnresolvedReferences
    reactor.run()
