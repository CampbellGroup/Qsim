from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from Qsim.clients.qtui.electrodewidget import ElectrodeIndicator
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
from PyQt4.Qt import QPushButton
from config.dac_8718_config import dac_8718_config
import numpy as np
from electrodes import Electrodes


class ElectrodeWedgeGUI():

    def __init__(self, channel_configuration, settings):
        self.name = channel_configuration.name
        self.dac_channel = channel_configuration.number
        self.octant = channel_configuration.number
        self.minval = channel_configuration.minval
        self.maxval = channel_configuration.maxval

        if self.octant == 0:
            self.is_plus_x = True
            self.is_plus_x = False
            self.is_minus_x = True
            self.is_minus_x = False
            self.is_minus_y = True
            self.is_minus_y = False
            self.is_plus_y = True
            self.is_plus_y = False
            self.is_plus_z = True
            self.is_minus_z = False
            self.is_plus_z = False
            self.is_minus_z = True

        self.setup_widget(settings)

    def setup_widget(self, settings):
        self.spinBox = QCustomSpinBox(self.name, (self.minval, self.maxval))

        try:
            self.init_voltage = settings[self.name]
            self.spinBox.spinLevel.setValue(self.init_voltage)
        except:
            self.init_voltage = 0.0
            self.spinBox.spinLevel.setValue(0.0)

        self.spinBox.setStepSize(0.001)
        self.spinBox.spinLevel.setDecimals(3)


class dacclient(QtGui.QWidget):

    def __init__(self, reactor, parent=None):

        super(dacclient, self).__init__()
        self.max_bit_value = 2**16 - 1
        self.min_bit_value = 0
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.config = dac_8718_config()
        self.minval = self.config.minval
        self.maxval = self.config.maxval
        self.step_size = 0.01
        self.connect()

    @inlineCallbacks
    def connect(self):

        from labrad.wrappers import connectAsync
        from labrad.units import WithUnit as U

        self.U = U
        self.cxn = yield connectAsync(name="dac8718 client")
        self.server = self.cxn.dac8718_server
        self.reg = self.cxn.registry
        yield self.get_settings()
        yield self.initialize_GUI()

    @inlineCallbacks
    def get_settings(self):

        self.settings = {}
        yield self.reg.cd('settings', True)
        self.keys = yield self.reg.dir()
        self.keys = self.keys[1]
        for key in self.keys:
            value = yield self.reg.get(key)
            self.settings[key] = value

    def initialize_GUI(self):

        self.layout = QtGui.QGridLayout()
        self.electrodes = []
        qBox = QtGui.QGroupBox('DAC Channels')

        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        self.layout.addWidget(qBox, 0, 0)

        self.electrode_indicator = ElectrodeIndicator(self.minval, self.maxval)

        self._add_dipole_widgets()
        self._add_quadrupole_widgets()

        res_box = QCustomSpinBox('Step Size', (0.0001, 3))
        res_box.setStepSize(0.001)
        res_box.spinLevel.setDecimals(3)
        res_box.spinLevel.setValue(self.step_size)
        res_box.spinLevel.valueChanged.connect(self.update_res)

        save_widget = QPushButton('Save values')
        save_widget.clicked.connect(self.save_to_registry)

        self.layout.addWidget(self.electrode_indicator, 0, 1, 1, 3)

        self.layout.addWidget(res_box, 9, 0)
        self.layout.addWidget(save_widget, 10, 0)

        for channel_config in self.config.channels:
            electrode = ElectrodeWedgeGUI(channel_config, self.settings)
            self.update_dac(electrode.init_voltage, channel_config.number, channel_config.number)

            self.electrodes.append(electrode)
            subLayout.addWidget(electrode.spinBox)
            e_connect = electrode.spinBox.spinLevel.valueChanged.connect
            e_connect(lambda value=electrode.spinBox.spinLevel.value(),
                      dac=channel_config.number,
                      octant=channel_config.octant:
                          self.update_dac(value, dac, octant))

        self.setLayout(self.layout)

    def _add_dipole_widgets(self):
        dipoles_names = ['Ex', 'Ey', 'Ez']
        self.dipoles = []
        for kk, dipole_name in enumerate(dipoles_names):
            # Value indicator.
            spinbox = QCustomSpinBox(dipole_name, (-10, 10))
            spinbox.setStepSize(0.001)
            spinbox.spinLevel.setDecimals(3)
            self.layout.addWidget(spinbox, 3, kk, 1, 1)
            self.dipoles.append(spinbox)
            # Up and down value control buttons
            up_name = dipole_name + ' up'
            up_button = QtGui.QPushButton(up_name)
            down_name = dipole_name + ' down'
            down_button = QtGui.QPushButton(down_name)
            multipole_change = self.change_multipole_moment
            up_button.clicked.connect(lambda: multipole_change(up_button))
            down_button.clicked.connect(lambda: multipole_change(down_button))
            self.layout.addWidget(up_button, 4, kk)
            self.layout.addWidget(down_button, 5, kk)

    def _add_quadrupole_widgets(self):
        quadrupole_names = ['Exx_yy', 'Ezz_xx_yy', 'Exy', 'Eyz', 'Ezx']
        for kk, quadrupole_name in enumerate(quadrupole_names):
            # Value indicator.
            spinbox = QCustomSpinBox(quadrupole_name, (-10, 10))
            spinbox.setStepSize(0.001)
            spinbox.spinLevel.setDecimals(3)
            self.layout.addWidget(spinbox, 8, kk, 1, 1)
            # Up and down value control buttons
            up_name = quadrupole_name + ' up'
            up_button = QtGui.QPushButton(up_name)
            down_name = quadrupole_name + ' down'
            down_button = QtGui.QPushButton(down_name)
            multipole_change = self.change_multipole_moment
            up_button.clicked.connect(lambda: multipole_change(up_button))
            down_button.clicked.connect(lambda: multipole_change(down_button))
            self.layout.addWidget(up_button, 6, kk)
            self.layout.addWidget(down_button, 7, kk)

    def change_multipole_moment(self, button):
        buttonname = button.text()
        if 'up' in buttonname:
            sign = 1
        else:
            sign = -1

        if 'Ex' in buttonname:
            voltage1 = []
            voltage2 = []
            for electrode in self.electrodes:
                voltage = electrode.spinBox.spinLevel.value()
                if electrode.octant in [1,5]:
                    voltage1.append(voltage - sign*self.step_size)
                    electrode.spinBox.spinLevel.setValue(voltage - sign*self.step_size)
                if electrode.octant in [3, 7]:
                    voltage2.append(voltage + sign*self.step_size)
                    electrode.spinBox.spinLevel.setValue(voltage + sign*self.step_size)
            Ex = np.mean(voltage1) - np.mean(voltage2)
            self.dipoles[0].spinLevel.setValue(-1*Ex)

        if 'Ey' in buttonname:
            voltage1 = []
            voltage2 = []
            for electrode in self.electrodes:
                voltage = electrode.spinBox.spinLevel.value()
                if electrode.octant in [2,6]:
                    voltage1.append(voltage - sign*self.step_size)
                    electrode.spinBox.spinLevel.setValue(voltage - sign*self.step_size)
                if electrode.octant in [4,8]:
                    voltage2.append(voltage + sign*self.step_size)
                    electrode.spinBox.spinLevel.setValue(voltage + sign*self.step_size)
            Ey = np.mean(voltage1) - np.mean(voltage2)
            self.dipoles[1].spinLevel.setValue(-1*Ey)

        if 'Ez' in buttonname:
            voltagetop = []
            voltagebottom = []
            for electrode in self.electrodes:
                voltage = electrode.spinBox.spinLevel.value()
                if electrode.octant in [1,2,3,4]:
                    voltagetop.append(voltage - sign*0.1)
                    electrode.spinBox.spinLevel.setValue(voltage - sign*self.step_size)
                if electrode.octant in [5,6,7,8]:
                    voltagebottom.append(voltage + sign*0.1)
                    electrode.spinBox.spinLevel.setValue(voltage + sign*self.step_size)
            Ez = np.mean(voltagetop) - np.mean(voltagebottom)
            self.dipoles[2].spinLevel.setValue(-1*Ez)

    def volt_to_bit(self, volt):
        m = (2**16 - 1)/(self.maxval - self.minval)
        b = -1 * self.minval * m
        bit = int(m*volt + b)
        return bit

    @inlineCallbacks
    def update_dac(self, voltage, dac, octant):

        bit = self.volt_to_bit(voltage)
        yield self.server.dacoutput(dac, bit)
        self.electrode_indicator.update_octant(octant, voltage)

    def update_res(self, res):
        """
        Changes the bit resolution.  This function will disappear when working
        with voltages and a proper transfer matrix.
        """
        self.step_size = res

    @inlineCallbacks
    def save_to_registry(self, pressed):
        for electrode in self.electrodes:
            value = electrode.spinBox.spinLevel.value()
            yield self.reg.set(electrode.name, value)

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    dacWidget = dacclient(reactor)
    dacWidget.show()
    reactor.run()  # @UndefinedVariable
