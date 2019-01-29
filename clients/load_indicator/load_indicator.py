'''
Created on Sep 21, 2016

@author: Anthony Ransford
'''

from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
import os


class indicator():

    def __init__(self, name, limits):
        self.label = QtGui.QLabel(name)
        self.limits = limits

    def update_value(self, value):
        if (value >= self.limits[0]) and (value <= self.limits[1]):
            self.label.setStyleSheet('color: green')
        else:
            self.label.setStyleSheet('color: red')


class LoadIndicator(QtGui.QWidget):

    indicators = {'369 Freq': [812.108, 812.112],
                  '399 Freq': [752.450, 752.453],
                  '935 Freq': [320.568, 320.572],
                  'DAC Working': [0.9, 1.1],
                  'Oven On': [0.9, 1.1]}

    def __init__(self, reactor):
        super(LoadIndicator, self).__init__()
        self.reactor = reactor
        self.connect()

    @inlineCallbacks
    def connect(self):

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.main_loop)
        self.timer.start(1000)

        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name='Load Indicator')
        self.cxnwlm = yield connectAsync('10.97.112.2',
                                         password=os.environ['LABRADPASSWORD'],
                                         name='Load Indicator')
        self.W7 = self.cxn.multiplexerserver
        self.wlm = self.cxnwlm.multiplexerserver

        yield self.wlm.signal__frequency_changed(546532)
        yield self.wlm.addListener(listener=self.update_frequency,
                                   source=None, ID=546532)

        self.dac = self.cxn.dac_ad660_server
        self.arduino_ttl = self.cxn.arduinottl
#        self.RFscope = self.cxn.ds1052e_scope_server
        self.kt = self.cxn.keithley_2230g_server
        self.kt.select_device(0)
        self.initialize_gui()

    def initialize_gui(self):
        layout = QtGui.QGridLayout()
        qbox = QtGui.QGroupBox('Load Indicator')
        sublayout = QtGui.QGridLayout()
        qbox.setLayout(sublayout)
        layout.addWidget(qbox, 0, 0)
        self.indwidgets = {}
        font = QtGui.QFont("ComicS", 18, QtGui.QFont.Bold)

        for i, item in enumerate(self.indicators):
            ind = indicator(item, self.indicators[item])
            ind.label.setStyleSheet('color: red')
            ind.label.setFont(font)
            self.indwidgets[item] = ind
            layout.addWidget(ind.label, 0, i)

        self.setLayout(layout)

    def update_frequency(self, c, signal):
        chan = signal[0]
        freq = signal[1]
        if chan == 4:
            self.indwidgets['935 Freq'].update_value(freq)

    @inlineCallbacks
    def main_loop(self):
        try:
            reflected = yield self.RFscope.measurevpp(1)
            forward = yield self.RFscope.measurevpp(2)
        except:
            reflected = 1000
            forward = 0.0

        try:
            WS7_freq = yield self.W7.get_frequency(1)
            if 812.0 < WS7_freq < 813.0:
                self.indwidgets['369 Freq'].update_value(WS7_freq)
            elif 752.0 < WS7_freq < 753.0:
                self.indwidgets['399 Freq'].update_value(WS7_freq)
        except:
            WS7_freq = 0.0

        try:
            volts = yield self.dac.get_analog_voltages()
            if len(volts) > 1:
                self.indwidgets['DAC Working'].update_value(1.0)
            else:
                self.indwidgets['DAC Working'].update_value(0.0)
        except:
            self.indwidgets['DAC Working'].update_value(0.0)

        oven_output = yield self.kt.current(3)
        if oven_output['A'] >= 1.0:
            self.indwidgets['Oven On'].update_value(1.0)
        else:
            self.indwidgets['Oven On'].update_value(0.0)

#        self.indwidgets['RF Power Foward'].update_value(float(forward))
#        self.indwidgets['RF reflected'].update_value(float(reflected))

    def closeEvent(self, x):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()
        self.reactor.stop()

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    LoadWidget = LoadIndicator(reactor)
    LoadWidget.show()
    reactor.run()
