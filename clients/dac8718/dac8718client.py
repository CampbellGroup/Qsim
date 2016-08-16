from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from Qsim.clients.qtui.electrodewidget import ElectrodeIndicator
from twisted.internet.defer import inlineCallbacks, returnValue
from PyQt4 import QtGui
from PyQt4.Qt import QPushButton
from config.dac_8718_config import dac_8718_config
import numpy as np
from electrodes import Electrodes


class ElectrodeWedgeGUI():

    def __init__(self, electrode):
        """
        Parameters
        ----------
        electrode: Electrode instance.
        """
        self.electrode = electrode
        self.name = electrode.name
        self.dac_channel = electrode.number
        self.octant = electrode.number
        self.minval = 0
        self.maxval = int(2**16) - 1

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

        self.setup_widget()

    def setup_widget(self, settings):
        self.spinBox = QCustomSpinBox(self.name, (self.minval, self.maxval))

        try:
            self.initial_bit_value = self.electrode.bit_value
        except:
            self.initial_bit_value = int(2**15)
        self.spinBox.spinLevel.setValue(self.initial_bit_value)

        self.spinBox.setStepSize(1)
        self.spinBox.spinLevel.setDecimals(1)


class DAC8718Client(QtGui.QWidget):

    def __init__(self, reactor, parent=None):

        super(DAC8718Client, self).__init__()
        self.electrodes = Electrodes()
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
        self.electrode_guis = []
        qBox = QtGui.QGroupBox('DAC Channels')

        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        self.layout.addWidget(qBox, 0, 0)

        self.electrode_indicator = ElectrodeIndicator(self.minval, self.maxval)

        self._add_dipole_widgets()
        self._add_quadrupole_widgets()

        step_size_box = QCustomSpinBox('Step Size', (0.0001, 3))
        step_size_box.setStepSize(0.001)
        step_size_box.spinLevel.setDecimals(3)
        step_size_box.spinLevel.setValue(self.step_size)
        step_size_box.spinLevel.valueChanged.connect(self.update_step_size)

        save_widget = QPushButton('Save values')
        save_widget.clicked.connect(self.save_to_registry)

        self.layout.addWidget(self.electrode_indicator, 0, 1, 1, 3)

        self.layout.addWidget(step_size_box, 9, 0)
        self.layout.addWidget(save_widget, 10, 0)

        for channel_config in self.config.channels:
            channel_name = channel_config.name
            initial_bit_value = self.settings[channel_name]
            electrode = self.electrodes.get_electrode(name=channel_name)
            electrode.bit_value = initial_bit_value

            electrode_gui = ElectrodeWedgeGUI(electrode=electrode)
            self.update_dac(electrode)
            self.update_dac(electrode_gui.init_voltage, channel_config.number,
                            channel_config.number)

            self.electrode_guis.append(electrode_gui)
            subLayout.addWidget(electrode_gui.spinBox)
#            e_connect = electrode_gui.spinBox.spinLevel.valueChanged.connect
#            e_connect(lambda value=electrode_gui.spinBox.spinLevel.value(),
#                      dac=channel_config.number,
#                      octant=channel_config.octant:
#                          self.update_dac(value, dac, octant))

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
        button_name = button.text()
        self._update_multipoles_from_button_name(button_name=button_name)
        self.electrodes.update_voltages_from_multipole_moments()
        self.update_all_dac_channels()

    def _update_multipoles_from_button_name(self, button_name):
        if 'up' in button_name:
            sign = 1
        else:
            sign = -1
        delta_value = sign * self.step_size

        multipole_name = self._multipole_name_from_button(button_name)

        multipole_moments = self.electrodes.multipole_moments
        current_value = multipole_moments.get_value(multipole_name)
        new_value = current_value + delta_value
        multipole_moments.set_value(name=multipole_name, value=new_value)

    def update_all_dac_channels(self):
        for electrode in self.electrodes.electrode_list:
            self.update_dac(electrode)

    def _multipole_name_from_button(button_name=None):
        """
        button_name: str
        """
        if button_name in ('Ex up', 'Ex down'):
            multipole_name = 'M_1'
        elif button_name in ('Ey up', 'Ey down'):
            multipole_name = 'M_2'
        elif button_name in ('Ez up', 'Ez down'):
            multipole_name = 'M_3'
        elif button_name in ('Exx_yy up', 'Exx_yy down'):
            multipole_name = 'M_4'
        elif button_name in ('Ezz_xx_yy up', 'Ezz_xx_yy down'):
            multipole_name = 'M_5'
        elif button_name in ('Exy up', 'Exy down'):
            multipole_name = 'M_6'
        elif button_name in ('Eyz up', 'Eyz down'):
            multipole_name = 'M_7'
        elif button_name in ('Ezx up', 'Ezx down'):
            multipole_name = 'M_8'
        return multipole_name

    @inlineCallbacks
    def update_dac(self, electrode):
        """
        Parameters
        ----------
        electrode: Electrode class instance.
        """
        yield self.server.dacoutput(electrode.number, electrode.bit_value)
        self.electrode_indicator.update_octant(electrode.octant,
                                               electrode.voltage)

    def update_step_size(self, step_size):
        """
        Changes the bit resolution.
        """
        self.step_size = step_size

    @inlineCallbacks
    def save_to_registry(self, pressed):
        for electrode_gui in self.electrode_guis:
            value = electrode_gui.spinBox.spinLevel.value()
            yield self.reg.set(electrode_gui.name, value)


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    dac_widget = DAC8718Client(reactor)
    dac_widget.show()
    reactor.run()  # @UndefinedVariable
