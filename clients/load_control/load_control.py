from common.lib.clients.qtui.switch import QCustomSwitchChannel
from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from common.lib.clients.qtui.timer import QCustomTimer
from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui
from pygame import mixer

SIGNALID = 112983


class LoadControl(QtGui.QWidget):

    def __init__(self, reactor, cxn=None):
        super(LoadControl, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        mixer.init()
        self.its_trap = mixer.Sound('/home/qsimexpcontrol/Music/trap.wav')
        self.vader = mixer.Sound('/home/qsimexpcontrol/Music/swvader01.wav')
        self.reactor = reactor
        self.kt = None
        self.bi_directional_state = False
        self.cxn = cxn
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions

        """
        from labrad.units import WithUnit as U
        self.U = U
        if self.cxn is None:
            self.cxn = yield connection(name="Load Control")
            yield self.cxn.connect()
        self.PMT = yield self.cxn.get_server('normalpmtflow')
        self.pv = yield self.cxn.get_server('parametervault')
        self.TTL = yield self.cxn.get_server('arduinottl')
        self.oven = yield self.cxn.get_server('ovenserver')
        self.reg = yield self.cxn.get_server('registry')
        try:
            yield self.reg.cd(['', 'settings'])
            self.settings = yield self.reg.dir()
            self.settings = self.settings[1]
        except ImportError:
            self.settings = []
        yield self.setup_listeners()
        yield self.initializeGUI()

    @inlineCallbacks
    def setup_listeners(self):
        yield self.PMT.signal__new_count(SIGNALID)
        yield self.PMT.addListener(listener=self.on_new_counts,
                                   source=None, ID=SIGNALID)

    @inlineCallbacks
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        self.shutter_widget = QCustomSwitchChannel('399/Oven/ProtectionBeam',
                                                   ('Open/Oven On', 'Closed/Oven Off'))
        self.shutter_widget.TTLswitch.toggled.connect(self.toggle)
        self.timer_widget = QCustomTimer('Loading Time', show_control=False)
        self.current_widget = QCustomSpinBox("Current ('A')", (0.0, 3.0))

        self.current_widget.setStepSize(0.01)
        self.current_widget.spinLevel.setDecimals(2)
        self.current_widget.spinLevel.valueChanged.connect(self.current_changed)

        if 'oven' in self.settings:
            value = yield self.reg.get('oven')
            self.current_widget.spinLevel.setValue(value)

        if '399 trapshutter' in self.settings:
            value = yield self.reg.get('399 trapshutter')
            value = bool(value)
            self.shutter_widget.TTLswitch.setChecked(value)
        else:
            self.shutter_widget.TTLswitch.setChecked(False)

        layout.addWidget(self.current_widget, 1, 1)
        layout.addWidget(self.shutter_widget, 0, 0)
        layout.addWidget(self.timer_widget, 0, 1)
        self.setLayout(layout)

    @inlineCallbacks
    def on_new_counts(self, signal, pmt_value):
        pass
        disc_value = yield self.pv.get_parameter('Loading', 'ion_threshold')  # this throws error on closeout since listner is yielding to server
        switch_on = self.shutter_widget.TTLswitch.isChecked()
        if (pmt_value >= disc_value) and switch_on:
            self.shutter_widget.TTLswitch.setChecked(False)
            self.its_trap.play()
        elif (self.timer_widget.time >= 600.0) and switch_on:
            self.vader.play()
            self.shutter_widget.TTLswitch.setChecked(False)

    @inlineCallbacks
    def toggle(self, value):
        yield self.changeState(value)
        if value:
            self.timer_widget.reset()
            self.timer_widget.start()
            yield self.oven.oven_output(True)
        else:
            yield self.oven.oven_output(False)
            self.timer_widget.reset()

    @inlineCallbacks
    def current_changed(self, value):
        yield self.oven.oven_current(self.U(value, 'A'))
        if 'oven' in self.settings:
            yield self.reg.set('oven', value)

    @inlineCallbacks
    def changeState(self, state):
        if '399 trapshutter' in self.settings:
            yield self.reg.set('399 trapshutter', state)
        yield self.TTL.ttl_output(10, state)

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    LoadControlWidget = LoadControl(reactor)
    LoadControlWidget.show()
    reactor.run()
