from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from clients.dac_control.electrode_widget import ElectrodeIndicator
from twisted.internet.defer import inlineCallbacks
from PyQt5.QtWidgets import *
from config.dac_ad660_config import HardwareConfiguration as HC
import logging
import time

logger = logging.getLogger(__name__)


class Electrode:

    def __init__(self, dac, minval, maxval, name=None):

        self.dac = dac
        self.minval = minval
        self.maxval = maxval
        if name:
            self.name = name
        else:
            self.name = str('DAC: ' + str(dac))
        self.setup_widget()

    def setup_widget(self):

        self.spinBox = QCustomSpinBox(self.name, (self.minval, self.maxval))
        self.init_voltage = 0.0
        self.spinBox.spinLevel.setValue(0.0)

        self.spinBox.setStepSize(0.0001)
        self.spinBox.spinLevel.setDecimals(4)


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

        print(self.init_voltages)
        print(self.init_multipoles)
        # logger.info(f"init_voltages:{self.init_voltages}")
        self.initialize_gui()

    def initialize_gui(self):
        layout = QVBoxLayout()

        # Make the grid of DAC input spinboxes
        self.electrodes = {}

        # Build the grid of electrodes

        dac_box = QGroupBox('DAC Channels')
        dac_layout = QGridLayout()
        dac_box.setLayout(dac_layout)

        length_of_column = 2
        for i, channel in enumerate(self.dac_channels):
            electrode = Electrode(channel.dac_channel_number,
                                  channel.allowed_voltage_range[0],
                                  channel.allowed_voltage_range[1],
                                  name=channel.name)
            self.electrodes[electrode.name] = electrode
            # noinspection PyArgumentList
            dac_layout.addWidget(electrode.spinBox, i % length_of_column, i // length_of_column)
            electrode.spinBox.spinLevel.setValue(self.init_voltages[channel.dac_channel_number])
            electrode.spinBox.spinLevel.valueChanged.connect(lambda value=electrode.spinBox.spinLevel.value(),
                                                                    elec=electrode: self.update_dac(value, elec))

        # Build the grid of multipoles

        multipole_box = QGroupBox('Multipoles')
        multipole_layout = QGridLayout()
        multipole_box.setLayout(multipole_layout)

        multipole_names = ['', '', 'EC_base', 'EC_Diff', 'RF', 'DC', 'DC_diff', 'RF_diff']
        self.multipoles = []
        j = 0
        length_of_column = 2
        for i, multipole in enumerate(multipole_names):
            spinbox = QCustomSpinBox(multipole, (-100, 100))
            spinbox.setStepSize(0.001)
            spinbox.spinLevel.setDecimals(3)
            spinbox.spinLevel.setValue(self.init_multipoles[i])
            spinbox.spinLevel.valueChanged.connect(self.change_multipole)
            multipole_layout.addWidget(spinbox, i % length_of_column, i // length_of_column)
            self.multipoles.append(spinbox)

        self.electrode_indicator = ElectrodeIndicator()
        for port, v in self.init_voltages.items():
            self.electrode_indicator.update_rod(port, v)

        layout.addWidget(self.electrode_indicator)
        layout.addWidget(dac_box)
        layout.addWidget(multipole_box)
        self.setLayout(layout)
        self.maximumSize()

    @inlineCallbacks
    def update_dac(self, voltage, electrode):
        dac = electrode.dac
        yield self.dacserver.set_individual_analog_voltages([(dac, voltage)])
        self.electrode_indicator.update_rod(dac, voltage)

    @inlineCallbacks
    def change_multipole(self, value):
        self.start = time.time()
        mvector = []
        for multipole in self.multipoles:
            mvector.append(multipole.spinLevel.value())
        evector = yield self.multipole_server.set_multipoles(mvector)
        if len(evector) == 8:
            for dac, voltage in enumerate(evector):

                electrode = list(self.electrodes.values())[dac]
                electrode.spinBox.spinLevel.setValue(voltage)
                self.electrode_indicator.update_rod(electrode.name, voltage)

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
