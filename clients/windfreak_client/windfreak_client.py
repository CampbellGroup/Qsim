from PyQt4 import QtGui, QtCore
from twisted.internet.defer import inlineCallbacks, returnValue
import socket
import os
from Qsim.clients.windfreak_client.windfreak_gui import QCustomWindfreakGui
import sys


class windfreak_client(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(windfreak_client, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, QtGui.QSizePolicy.MinimumExpanding)
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
        layout = QtGui.QVBoxLayout()

        self.gui = QCustomWindfreakGui()

        init_freq = yield self.server.get_freq(0)
        init_power = yield self.server.get_power(0)
        init_onoff = yield self.server.get_enable(0)
        init_sweep_low = yield self.server.get_sweep_freq_low(0)
        init_sweep_high = yield self.server.get_sweep_freq_high(0)
        init_sweep_freq_step = yield self.server.get_sweep_freq_step(0)
        init_sweep_time_step = yield self.server.get_sweep_time_step(0)
        init_sweep_onoff = yield self.server.get_sweep_cont(0)
        init_sweep_low_power = yield self.server.get_sweep_power_low(0)
        init_sweep_high_power = yield self.server.get_sweep_power_high(0)
        init_sweep_single = yield self.server.get_sweep_single(0)

        self.gui.a.freq_input.spinLevel.setValue(float(init_freq))
        self.gui.a.power_input.spinLevel.setValue(float(init_power))
        self.gui.a.onoff_button.setDown(init_onoff)
        self.gui.a.sweep_low_freq_input.spinLevel.setValue(float(init_sweep_low))
        self.gui.a.sweep_high_freq_input.spinLevel.setValue(float(init_sweep_high))
        self.gui.a.sweep_freq_step_input.spinLevel.setValue(float(init_sweep_freq_step))
        self.gui.a.sweep_time_step_input.spinLevel.setValue(float(init_sweep_time_step))
        self.gui.a.sweep_onoff_button.setDown(init_sweep_onoff)
        self.gui.a.sweep_low_power_input.spinLevel.setValue(float(init_sweep_low_power))
        self.gui.a.sweep_high_power_input.spinLevel.setValue(float(init_sweep_high_power))
        self.gui.a.sweep_single_onoff_button.setDown(init_sweep_single)

        self.gui.a.freq_input.spinLevel.valueChanged.connect(
            lambda: self.changeFreq(0, float(self.gui.a.freq_input.spinLevel.text())))
        self.gui.a.power_input.spinLevel.valueChanged.connect(
            lambda: self.changePower(0, float(self.gui.a.power_input.spinLevel.text())))
        self.gui.a.onoff_button.toggled.connect(
            lambda: self.toggle_onoff(0, self.gui.a.onoff_button.isDown()))
        self.gui.a.sweep_low_power_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepLowPower(0, float(self.gui.a.sweep_low_power_input.spinLevel.text())))
        self.gui.a.sweep_high_power_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepHighPower(0, float(self.gui.a.sweep_high_power_input.spinLevel.text())))
        self.gui.a.sweep_low_freq_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepLowLim(0, float(self.gui.a.sweep_low_freq_input.spinLevel.text())))
        self.gui.a.sweep_high_freq_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepHighLim(0, float(self.gui.a.sweep_high_freq_input.spinLevel.text())))
        self.gui.a.sweep_freq_step_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepFreqStep(0, float(self.gui.a.sweep_freq_step_input.spinLevel.text())))
        self.gui.a.sweep_time_step_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepTimeStep(0, float(self.gui.a.sweep_time_step_input.spinLevel.text())))
        self.gui.a.sweep_onoff_button.toggled.connect(
            lambda state=self.gui.a.sweep_onoff_button.isDown(): self.toggle_sweep(0, state))
        self.gui.a.sweep_single_onoff_button.toggled.connect(
            lambda state=self.gui.a.sweep_single_onoff_button.isDown(): self.toggle_sweep_single(0, state))

        init_freq = yield self.server.get_freq(1)
        init_power = yield self.server.get_power(1)
        init_onoff = yield self.server.get_enable(1)
        init_sweep_low = yield self.server.get_sweep_freq_low(1)
        init_sweep_high = yield self.server.get_sweep_freq_high(1)
        init_sweep_freq_step = yield self.server.get_sweep_freq_step(1)
        init_sweep_time_step = yield self.server.get_sweep_time_step(1)
        init_sweep_onoff = yield self.server.get_sweep_cont(1)
        init_sweep_low_power = yield self.server.get_sweep_power_low(1)
        init_sweep_high_power = yield self.server.get_sweep_power_high(1)
        init_sweep_single = yield self.server.get_sweep_single(1)

        self.gui.b.freq_input.spinLevel.setValue(float(init_freq))
        self.gui.b.power_input.spinLevel.setValue(float(init_power))
        self.gui.b.onoff_button.setDown(init_onoff)
        self.gui.b.sweep_low_freq_input.spinLevel.setValue(float(init_sweep_low))
        self.gui.b.sweep_high_freq_input.spinLevel.setValue(float(init_sweep_high))
        self.gui.b.sweep_freq_step_input.spinLevel.setValue(float(init_sweep_freq_step))
        self.gui.b.sweep_time_step_input.spinLevel.setValue(float(init_sweep_time_step))
        self.gui.b.sweep_onoff_button.setDown(init_sweep_onoff)
        self.gui.b.sweep_low_power_input.spinLevel.setValue(float(init_sweep_low_power))
        self.gui.b.sweep_high_power_input.spinLevel.setValue(float(init_sweep_high_power))
        self.gui.b.sweep_single_onoff_button.setDown(init_sweep_single)

        self.gui.b.freq_input.spinLevel.valueChanged.connect(
            lambda: self.changeFreq(1, float(self.gui.b.freq_input.spinLevel.text())))
        self.gui.b.power_input.spinLevel.valueChanged.connect(
            lambda: self.changePower(1, float(self.gui.b.power_input.spinLevel.text())))
        self.gui.b.onoff_button.toggled.connect(
            lambda state=self.gui.a.onoff_button.isDown(): self.toggle_onoff(1, state))
        self.gui.b.sweep_low_power_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepLowPower(1, float(self.gui.b.sweep_low_power_input.spinLevel.text())))
        self.gui.b.sweep_high_power_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepHighPower(1, float(self.gui.b.sweep_high_power_input.spinLevel.text())))
        self.gui.b.sweep_low_freq_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepLowLim(1, float(self.gui.b.sweep_low_freq_input.spinLevel.text())))
        self.gui.b.sweep_high_freq_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepHighLim(1, float(self.gui.b.sweep_high_freq_input.spinLevel.text())))
        self.gui.b.sweep_freq_step_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepFreqStep(1, float(self.gui.b.sweep_freq_step_input.spinLevel.text())))
        self.gui.b.sweep_time_step_input.spinLevel.valueChanged.connect(
            lambda: self.changeSweepTimeStep(1, float(self.gui.b.sweep_time_step_input.spinLevel.text())))
        self.gui.b.sweep_onoff_button.toggled.connect(
            lambda state=self.gui.a.sweep_onoff_button.isDown(): self.toggle_sweep(1, state))
        self.gui.b.sweep_single_onoff_button.toggled.connect(
            lambda state=self.gui.a.sweep_single_onoff_button.isDown(): self.toggle_sweep_single(1, state))

        layout.addWidget(self.gui)
        # layout.minimumSize()
        self.setLayout(layout)

    @inlineCallbacks
    def sweepSingle_on(self, chan):
        yield self.server.set_sweep_single(chan, True)
        self.set_text_sweepSingleon(chan)

    @inlineCallbacks
    def sweepSingle_off(self, chan):
        yield self.server.set_sweep_single(chan, False)
        self.set_text_sweepSingleoff(chan)

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
    def toggle_onoff(self, chan, state):
        yield self.server.set_enable(chan, state)

    @inlineCallbacks
    def toggle_sweep(self, chan, state):
        yield self.server.set_sweep_cont(chan, state)

    @inlineCallbacks
    def toggle_sweep_single(self, chan, state):
        yield self.server.set_sweep_single(chan, state)


if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor

    client_inst = windfreak_client(reactor)
    client_inst.show()
    run = reactor.run()

