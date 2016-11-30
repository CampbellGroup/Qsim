'''
Created on Sep 21, 2016

@author: Anthony Ransford
'''

from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall


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

    indicators = {'369 Freq': [811.291, 811.2915],
                  '399 Freq': [751.52670, 751.5269],
                  '935 Freq': [320.57162, 320.57168],
                  'RF Power Foward': [2.8, 3.2],
                  'RF reflected': [0., 0.09]}

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
        self.cxnwlm = yield connectAsync('10.97.112.2', password='lab',
                                         name='Load Indicator')
        self.wlm = self.cxnwlm.multiplexerserver

        yield self.wlm.signal__frequency_changed(546532)
        yield self.wlm.addListener(listener=self.update_frequency,
                                   source=None, ID=546532)

        self.arduino_ttl = self.cxn.arduinottl
        self.RFscope = self.cxn.ds1052e_scope_server
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
        if chan == 8:
            self.indwidgets['399 Freq'].update_value(freq)
        if chan == 9:
            self.indwidgets['369 Freq'].update_value(freq)

    @inlineCallbacks
    def main_loop(self):
        reflected = yield self.RFscope.measurevpp(1)
        forward = yield self.RFscope.measurevpp(2)
        self.indwidgets['RF Power Foward'].update_value(float(forward))
        self.indwidgets['RF reflected'].update_value(float(reflected))

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
