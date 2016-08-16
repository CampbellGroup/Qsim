from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from Qsim.clients.qtui.electrodewidget import ElectrodeIndicator
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
from PyQt4.Qt import QPushButton
from config.dac_8718_config import dac_8718_config
import numpy as np


class Electrode():

    def __init__(self, dac, octant, minval, maxval, settings):

        self.dac = dac
        self.octant = octant
        self.minval = minval
        self.maxval = maxval
        self.name = 'DAC: ' + str(dac)

        if octant == 1:
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

        layout = QtGui.QGridLayout()
        self.electrodes = []
        qBox = QtGui.QGroupBox('DAC Channels')

        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)

        self.electrode_indicator = ElectrodeIndicator(self.minval, self.maxval)
        dipoles_names = ['Ex', 'Ey', 'Ez']
        self.dipoles = []
        for i, dipole in enumerate(dipoles_names):
            spinbox = QCustomSpinBox(dipole, (-10, 10))
            spinbox.setStepSize(0.001)
            spinbox.spinLevel.setDecimals(3)
            layout.addWidget(spinbox, 3, i + 1, 1, 1)
            self.dipoles.append(spinbox)

        res_box = QCustomSpinBox('Step Size', (0.0001,3))
        res_box.setStepSize(0.001)
        res_box.spinLevel.setDecimals(3)
        res_box.spinLevel.setValue(self.step_size)
        res_box.spinLevel.valueChanged.connect(self.update_res)

        save_widget = QPushButton('Save current values to Registry')
        save_widget.clicked.connect(self.save_to_registry)

        Ex_increase = QtGui.QPushButton('Ex Increase')
        Ex_decrease = QtGui.QPushButton('Ex Decrease')

        Ey_increase = QtGui.QPushButton('Ey Increase')
        Ey_decrease = QtGui.QPushButton('Ey Decrease')

        Ez_increase = QtGui.QPushButton('Ez Increase')
        Ez_decrease = QtGui.QPushButton('Ez Decrease')

        Ex_increase.clicked.connect(lambda: self.change_dipole(Ex_increase))
        Ey_increase.clicked.connect(lambda: self.change_dipole(Ey_increase))
        Ez_increase.clicked.connect(lambda: self.change_dipole(Ez_increase))

        Ex_decrease.clicked.connect(lambda: self.change_dipole(Ex_decrease))
        Ey_decrease.clicked.connect(lambda: self.change_dipole(Ey_decrease))
        Ez_decrease.clicked.connect(lambda: self.change_dipole(Ez_decrease))

        layout.addWidget(self.electrode_indicator, 0, 1, 1,3)
        layout.addWidget(Ex_increase, 5,3)
        layout.addWidget(Ex_decrease, 5,1)
        layout.addWidget(Ey_increase, 4,2)
        layout.addWidget(Ey_decrease, 6,2)

        layout.addWidget(Ez_increase, 4,0)
        layout.addWidget(Ez_decrease, 5,0)

        layout.addWidget(res_box, 6,0)
        layout.addWidget(save_widget, 7,0)

        for channel in self.config.channels:
            electrode = Electrode(channel.dac_chan, channel.octant,
                                  self.minval, self.maxval, self.settings)
            self.update_dac(electrode.init_voltage, channel.dac_chan, channel.octant)

            self.electrodes.append(electrode)
            subLayout.addWidget(electrode.spinBox)
            electrode.spinBox.spinLevel.valueChanged.connect(lambda value = electrode.spinBox.spinLevel.value(),
                                                             dac = channel.dac_chan,
                                                             octant = channel.octant :self.update_dac(value, dac, octant))

        self.setLayout(layout)

    def change_dipole(self, button):
        buttonname = button.text()
        if 'Increase' in buttonname:
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
