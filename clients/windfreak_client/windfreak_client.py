from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue
import socket
import os
from Qsim.clients.windfreak_client.windfreak_gui import QCustomWindfreakGui
import sys


class windfreak_client(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(windfreak_client, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.channel = {}
        self.channel_GUIs = {}
        self.connect()
        self.active_channel = 0

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.password = os.environ['LABRADPASSWORD']
        self.cxn = yield connectAsync('localhost', name=socket.gethostname() \
                                                        + 'Windfreak GUI', password=self.password)
        self.server = self.cxn.windfreak
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):
        layout = QtGui.QGridLayout()

        self.gui = QCustomWindfreakGui()
        try:
            init_freq = yield self.server.get_freq(0)
            init_power = yield self.server.get_power(0)
            init_chan = yield self.server.get_channel()
            init_onoff = yield self.server.get_onoff(0)
            init_sweep_low = yield self.server.get_sweep_freq_low(0)
            init_sweep_high = yield self.server.get_sweep_freq_high(0)
            init_sweep_freq_step = yield self.server.get_sweep_freq_step(0)
            init_sweep_time_step = yield self.server.get_sweep_time_step(0)
            init_sweep_onoff = yield self.server.get_sweep_cont(0)
            init_sweep_low_power = yield self.server.get_sweep_power_low(0)
            init_sweep_high_power = yield self.server.get_sweep_power_high(0)
            init_sweep_single = yield self.server.get_sweep_single(0)
            self.gui.a.freqInput.setText(str(init_freq))
            self.gui.a.powerInput.setText(str(init_power))
            self.gui.a.chanNotif.setText(str(init_chan))
            self.gui.a.onoffNotif.setText(str(init_onoff))
            self.gui.a.sweepLowLimInput.setText(str(init_sweep_low))
            self.gui.a.sweepHighLimInput.setText(str(init_sweep_high))
            self.gui.a.sweepFreqStepInput.setText(str(init_sweep_freq_step))
            self.gui.a.sweepTimeStepInput.setText(str(init_sweep_time_step))
            self.gui.a.sweeponoffNotif.setText(str(init_sweep_onoff))
            self.gui.a.sweepLowPowerInput.setText(str(init_sweep_low_power))
            self.gui.a.sweepHighPowerInput.setText(str(init_sweep_high_power))
            self.gui.a.sweepSingleNotif.setText(str(init_sweep_single))
        except Exception:
            pass

        self.gui.a.freq_conf_button.clicked.connect(lambda: self.changeFreq(0, float(self.gui.a.freqInput.text())))
        self.gui.a.freqInput.valueChanged.connect(lambda: self.changeFreq(0, float(self.gui.a.freqInput.text())))
        self.gui.a.power_conf_button.clicked.connect(lambda: self.changePower(0, float(self.gui.a.powerInput.text())))
        self.gui.a.powerInput.valueChanged.connect(lambda: self.changePower(0, float(self.gui.a.freqInput.text())))
        self.gui.a.on_button.clicked.connect(lambda: self.on(0))
        self.gui.a.off_button.clicked.connect(lambda: self.off(0))
        self.gui.a.sweepLowLim_conf_button.clicked.connect(lambda: self.changeSweepLowLim(0, float(self.gui.a.sweepLowLimInput.text())))
        self.gui.a.sweepHighLim_conf_button.clicked.connect(lambda: self.changeSweepHighLim(0, float(self.gui.a.sweepHighLimInput.text())))
        self.gui.a.sweepFreqStep_conf_button.clicked.connect(lambda: self.changeSweepFreqStep(0, float(self.gui.a.sweepFreqStepInput.text())))
        self.gui.a.sweepTimeStep_conf_button.clicked.connect(lambda: self.changeSweepTimeStep(0, float(self.gui.a.sweepTimeStepInput.text())))
        self.gui.a.sweepon_button.clicked.connect(lambda: self.sweep_on(0))
        self.gui.a.sweepoff_button.clicked.connect(lambda: self.sweep_off(0))
        self.gui.a.sweepLowPower_conf_button.clicked.connect(lambda: self.changeSweepLowPower(0, float(self.gui.a.sweepLowPowerInput.text())))
        self.gui.a.sweepSingleon_button.clicked.connect(lambda: self.sweepSingle_on(0))
        self.gui.a.sweepSingleoff_button.clicked.connect(lambda: self.sweepSingle_off(0))

        self.gui.b.freq_conf_button.clicked.connect(lambda: self.changeFreq(1, float(self.gui.b.freqInput.text())))
        self.gui.b.freqInput.valueChanged.connect(lambda: self.changeFreq(1, float(self.gui.b.freqInput.text())))
        self.gui.b.power_conf_button.clicked.connect(lambda: self.changePower(1, float(self.gui.b.powerInput.text())))
        self.gui.b.powerInput.valueChanged.connect(lambda: self.changePower(1, float(self.gui.b.freqInput.text())))
        self.gui.b.on_button.clicked.connect(lambda: self.on(1))
        self.gui.b.off_button.clicked.connect(lambda: self.off(1))
        self.gui.b.sweepLowLim_conf_button.clicked.connect(lambda: self.changeSweepLowLim(1, float(self.gui.a.sweepLowLimInput.text())))
        self.gui.b.sweepHighLim_conf_button.clicked.connect(lambda: self.changeSweepHighLim(1, float(self.gui.a.sweepHighLimInput.text())))
        self.gui.b.sweepFreqStep_conf_button.clicked.connect(lambda: self.changeSweepFreqStep(1, float(self.gui.a.sweepFreqStepInput.text())))
        self.gui.b.sweepTimeStep_conf_button.clicked.connect(lambda: self.changeSweepTimeStep(1, float(self.gui.a.sweepTimeStepInput.text())))
        self.gui.b.sweepon_button.clicked.connect(lambda: self.sweep_on(1))
        self.gui.b.sweepoff_button.clicked.connect(lambda: self.sweep_off(1))
        self.gui.b.sweepHighPower_conf_button.clicked.connect(lambda: self.changeSweepHighPower(0, float(self.gui.a.sweepHighPowerInput.text())))
        self.gui.b.sweepSingleon_button.clicked.connect(lambda: self.sweepSingle_on(1))
        self.gui.b.sweepSingleoff_button.clicked.connect(lambda: self.sweepSingle_off(1))

        print('connected')

        layout.addWidget(self.gui, 1, 1)
        # layout.minimumSize()
        self.setLayout(layout)

    def changeONOFF(self, chan):
        if chan == 0:
            self.gui.a.onoffNotif.setText('?')
        else:
            self.gui.b.onoffNotif.setText('?')

    @inlineCallbacks
    def sweepSingle_on(self, chan):
        yield self.server.set_sweep_single(chan, True)
        self.set_text_sweepSingleon(chan)

    @inlineCallbacks
    def sweepSingle_off(self, chan):
        yield self.server.set_sweep_single(chan, False)
        self.set_text_sweepSingleoff(chan)

    def set_text_sweepSingleon(self, chan):
        if chan == 0:
            self.gui.a.sweepSingleonoffNotif.setText('ON')
        else:
            self.gui.b.sweepSingleonoffNotif.setText('ON')

    def set_text_sweepSingleoff(self, chan):
        if chan == 0:
            self.gui.a.sweepSingleonoffNotif.setText('OFF')
        else:
            self.gui.b.sweepSingleonoffNotif.setText('OFF')

    @inlineCallbacks
    def changeSweepLowPower(self, chan, num):
        yield self.server.set_sweep_power_low(chan, num)

    @inlineCallbacks
    def changeSweepHighPower(self, chan, num):
        yield self.server.set_sweep_power_high(chan, num)

    @inlineCallbacks
    def changeSweepLowLim(self, chan, num):
        yield self.server.set_sweep_freq_low(chan, num)

    @inlineCallbacks
    def changeSweepHighLim(self, chan, num):
        yield self.server.set_sweep_freq_high(chan, num)

    @inlineCallbacks
    def changeSweepFreqStep(self, chan, num):
        yield self.server.set_sweep_freq_step(chan, num)

    @inlineCallbacks
    def changeSweepTimeStep(self, chan, num):
        yield self.server.set_sweep_time_step(chan, num)

    @inlineCallbacks
    def changeFreq(self, chan, num):
        yield self.server.set_freq(chan, num)

    @inlineCallbacks
    def changePower(self, chan, num):
        yield self.server.set_power(chan, num)

    @inlineCallbacks
    def on(self, chan):
        yield self.server.set_enable(chan, True)
        self.set_text_on(chan)

    def set_text_on(self, chan):
        if chan == 0:
            self.gui.a.onoffNotif.setText('ON')
        else:
            self.gui.b.onoffNotif.setText('ON')

    @inlineCallbacks
    def off(self, chan):
        yield self.server.set_enable(chan, False)
        self.set_text_off(chan)

    def set_text_off(self, chan):
        if chan == 0:
            self.gui.a.onoffNotif.setText('OFF')
        else:
            self.gui.b.onoffNotif.setText('OFF')

    @inlineCallbacks
    def sweep_on(self, chan):
        yield self.server.set_sweep_cont(chan, True)
        self.set_sweep_text_on(chan)

    def set_sweep_text_on(self, chan):
        if chan == 0:
            self.gui.a.sweeponoffNotif.setText('ON')
        else:
            self.gui.b.sweeponoffNotif.setText('ON')

    @inlineCallbacks
    def sweep_off(self, chan):
        yield self.server.set_sweep_cont(chan, False)
        self.set_sweep_text_off(chan)

    def set_sweep_text_off(self, chan):
        if chan == 0:
            self.gui.a.sweeponoffNotif.setText('OFF')
        else:
            self.gui.b.sweeponoffNotif.setText('OFF')


if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor

    client_inst = windfreak_client(reactor)
    client_inst.show()
    reactor.run()
