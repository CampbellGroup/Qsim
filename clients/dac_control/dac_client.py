from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from Qsim.clients.qtui.electrode_widget import ElectrodeIndicator
from twisted.internet.defer import inlineCallbacks
from PyQt5.QtWidgets import *
from config.dac_ad660_config import HardwareConfiguration as HC
import logging

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
        self.elec_dict = HC.elec_dict
        self.cxn = yield connectAsync(name="dac client")
        self.dacserver = self.cxn.dac_ad660_server
        self.init_voltages = yield self.dacserver.get_analog_voltages()
        # logger.info(f"init_voltages:{self.init_voltages}")
        self.initialize_gui()

    def initialize_gui(self):
        layout = QVBoxLayout()
        self.electrode_indicator = ElectrodeIndicator()

        # Make the grid of DAC input spinboxes
        grid_layout = QGridLayout()
        self.electrodes = {}
        q_box = QGroupBox('DAC Channels')

        sublayout = QGridLayout()
        q_box.setLayout(sublayout)
        grid_layout.addWidget(q_box, 0, 0)

        # The length of columns.
        # So if length_of_column was 2, and I had 6 DACs, I'd have 3 columns
        length_of_column = 2

        for i, (key, channel) in enumerate(self.elec_dict.items()):
            electrode = Electrode(channel.dac_channel_number,
                                  channel.allowed_voltage_range[0],
                                  channel.allowed_voltage_range[1],
                                  name=channel.name)
            self.electrodes[electrode.name] = electrode
            # noinspection PyArgumentList
            sublayout.addWidget(electrode.spinBox, i % length_of_column, i // length_of_column)
            # electrode.spinBox.spinLevel.setValue(self.init_voltages[channel.name])
            electrode.spinBox.spinLevel.valueChanged.connect(lambda value=electrode.spinBox.spinLevel.value(),
                                                                    elec=electrode: self.update_dac(value, elec))

        layout.addWidget(self.electrode_indicator)
        layout.addLayout(grid_layout)
        self.setLayout(layout)
        self.maximumSize()

    @inlineCallbacks
    def update_dac(self, voltage, electrode):
        if len(str(electrode.dac)) == 1:
            dac = '0' + str(electrode.dac)
        else:
            dac = str(electrode.dac)
        yield self.dacserver.set_individual_analog_voltages([(dac, voltage)])
        self.electrode_indicator.update_rod(dac, voltage)

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
