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
        self.name = str('DAC: ' + str(dac))
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
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.config = dac_8718_config()
        print self.config
        self.minval = self.config.minval
        self.maxval = self.config.maxval
        self.M = self.config.M
        self.U = self.config.U
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
        
        self.electrodeind = ElectrodeIndicator([-12,12])
        multipole_names = ['Ex', 'Ey', 'Ez', 'M1', 'M2', 'M3', 'M4', 'M5']
        self.multipoles = []
        j = 0
        for i, multipole in enumerate(multipole_names):
            if i >= 4: 
                j = 1
                i = i - 4
            spinbox = QCustomSpinBox(multipole, (-10, 10))
            spinbox.setStepSize(0.001)
            spinbox.spinLevel.setDecimals(3)
            spinbox.spinLevel.valueChanged.connect(self.change_multipole)
            layout.addWidget(spinbox, 3 + j, i + 1, 1, 1)
            self.multipoles.append(spinbox)
        
        layout.addWidget(self.electrodeind, 0, 1, 1,3)
        
        for channel in self.config.channels:
            electrode = Electrode(channel.dac, channel.octant,
                                  self.minval, self.maxval, self.settings)
            self.update_dac(electrode.init_voltage, channel)
            
            self.electrodes.append(electrode)
            subLayout.addWidget(electrode.spinBox)
            electrode.spinBox.spinLevel.valueChanged.connect(lambda value = electrode.spinBox.spinLevel.value(),
                                                             electrode = electrode :self.update_dac(value, electrode))

        self.setLayout(layout)
        
    def change_multipole(self):
        Mvector = []
        for multipole in self.multipoles:
            Mvector.append(multipole.spinLevel.value())
        Mvector = np.array(Mvector)
        Evector =  self.M.dot(Mvector)
        
        if max(Evector) >= self.maxval:
            return
        if min(Evector) <= self.minval:
            return
        
        for i, voltage in enumerate(Evector):
            self.update_dac(voltage, self.electrodes[i])
            self.electrodes[i].spinBox.spinLevel.setValue(voltage)
        
    def volt_to_bit(self, volt):
        m = (2**16 - 1)/(self.maxval - self.minval)
        b = -1 * self.minval * m
        bit = int(m*volt + b)
        return bit

    @inlineCallbacks     
    def update_dac(self, voltage, electrode):

        bit = self.volt_to_bit(voltage)    
        yield self.server.dacoutput(electrode.dac, bit)
        self.electrodeind.update_octant(electrode.octant, voltage)  
                   
if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    dacWidget = dacclient(reactor)
    dacWidget.show()
    reactor.run()  # @UndefinedVariable
