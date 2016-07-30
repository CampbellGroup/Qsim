from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from Qsim.clients.qtui.electrodewidget import ElectrodeIndicator 
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui
from PyQt4.Qt import QPushButton
from config.dac_8718_config import dac_8718_config
import numpy as np


class Electrode():
    
    def __init__(self, dac, pos, minval, maxval, settings):
        
        self.dac = dac
        self.pos = pos
        self.minval = minval
        self.maxval = maxval
        self.current_voltage
        self.name = 'DAC: ' + str(dac)
        
        if ((pos[0] == 1) and (pos[1] == 1)):
            self.is_plus_x = True
        else:
            self.is_plus_x = False
            
        if ((pos[0] == -1) and (pos[1] == -1)):
            self.is_minus_x = True
        else:
            self.is_minus_x = False
            
        if ((pos[0] == 1) and (pos[1] == -1)):
            self.is_minus_y = True
        else:
            self.is_minus_y = False
            
        if ((pos[0] == -1) and (pos[1] == 1)):
            self.is_plus_y = True
        else:
            self.is_plus_y = False
            
        if pos[2] == 1:
            self.is_plus_z = True
            self.is_minus_z = False
        else:
            self.is_plus_z = False
            self.is_minus_z = True
                    
        self.setup_widget(settings)
        
    def setup_widget(self, settings):
        
        self.spinBox = QCustomSpinBox(self.name, (self.minval, self.maxval))
        
        try:
            value = settings[self.name] 
            self.spinBox.spinLevel.setValue(value)
        except:
            self.spinBox.spinLevel.setValue(0.0)

        self.spinBox.setStepSize(0.001)
        self.spinBox.spinLevel.setDecimals(3)


class dacclient(QtGui.QWidget):

    def __init__(self, reactor, parent=None):

        super(dacclient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.config = dac_8718_config()
        self.minval = self.config.minval
        self.maxval = self.config.maxval
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

    @inlineCallbacks
    def initialize_GUI(self):

        layout = QtGui.QGridLayout()
        self.electrodes = []
        qBox = QtGui.QGroupBox('DAC Channels')
        
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)
        
        self.electrodeind = ElectrodeIndicator([-12,12])
        dipoles_names = ['Ex', 'Ey', 'Ez']
        self.dipoles = []
        for i, dipole in enumerate(dipoles_names):
            spinbox = QCustomSpinBox(dipole, (-10, 10))
            spinbox.setStepSize(0.001)
            spinbox.spinLevel.setDecimals(3)
            spinbox.spinLevel.valueChanged.connect(self.on_dipole_changed)
            layout.addWidget(spinbox, 3, i + 1, 1, 1)
            self.dipoles.append(spinbox)
        
        layout.addWidget(self.electrodeind, 0, 1, 1,3)

        for channel in self.config.channels:
            electrode = Electrode(channel.dac_chan, channel.elec_pos,
                                  self.minval, self.maxval, self.settings)
            self.electrodes.append(electrode)
            subLayout.addWidget(electrode.spinBox)
            electrode.spinBox.spinLevel.valueChanged.connect(self.on_dac_change)
        yield None

        self.setLayout(layout)
    
    @inlineCallbacks    
    def on_dac_change(self, value):

        plusxvals = [] 
        minusxvals = []
        plusyvals = []
        minusyvals = []
        for electrode in self.electrodes:
            voltage = electrode.spinBox.spinLevel.value()
            bit = self.volt_to_bit(voltage)
            
            yield self.server.dacoutput(electrode.dac, bit)
            
            if electrode.is_plus_x:
                plusxvals.append(voltage)
            elif electrode.is_minus_x:
                minusxvals.append(voltage)
            elif electrode.is_plus_y:
                plusyvals.append(voltage)
            elif electrode.is_minus_y:
                minusyvals.append(voltage)
                
        self.electrodeind.update_electrode(1,np.mean(plusxvals))
        self.electrodeind.update_electrode(2,np.mean(plusyvals))
        self.electrodeind.update_electrode(3,np.mean(minusxvals))
        self.electrodeind.update_electrode(4,np.mean(minusyvals))
        
    def on_dipole_changed(self, value):
        for dipole in self.dipoles:
            xvals = []
            yvals = []
            zvals = []
            
            if dipole.title.text() == 'Ex':
                for electrode in self.electrodes:
                    voltage = electrode.spinBox.spinLevel.value()
                    if (electrode.is_plus_x or electrode.is_minus_x):
                        xvals.append(voltage)
                meanx = np.mean(xvals)
                plusx = meanx - value
                minusx = meanx + value
                               
    def volt_to_bit(self, volt):
        m = (2**16 - 1)/(self.maxval - self.minval)
        b = -1 * self.minval * m
        bit = int(m*volt + b)
        return bit
                                           
if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    dacWidget = dacclient(reactor)
    dacWidget.show()
    reactor.run()  # @UndefinedVariable
