from common.lib.clients.qtui.switch import QCustomSwitchChannel
from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from common.lib.clients.qtui.timer import QCustomTimer
from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui
from twisted.internet.task import LoopingCall

SIGNALID = 123456


class LoadControl(QtGui.QWidget):

    def __init__(self, reactor, cxn=None):
        super(LoadControl, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.kt = None
        self.cxn = cxn
        self.connect()
        self.loop = LoopingCall(self.measure)
        self.loop.start(0.5)

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
        self.TTL = yield self.cxn.get_server('arduinottl')
        self.oven = yield self.cxn.get_server('ovenserver')
        #self.kt = yield self.cxn.get_server('keithley_2230g_server')
        #self.dv = yield self.cxn.get_server('data_vault')
        #self.grapher = yield self.cxn.get_server('grapher')
        self.reg = yield self.cxn.get_server('registry')
        #yield self.kt.select_device(0)
        #current = yield self.kt.current(3)

        #yield self.dv.cd(['oven_temp'], True)
        #self.ds = yield self.dv.new('oven_resistance', [('Time', 'seconds')],[('','resistance','mOhms')])
        #yield self.grapher.plot(self.ds, 'oven_resistance')
        try:
            yield self.reg.cd(['', 'settings'])
            self.settings = yield self.reg.dir()
            self.settings = self.settings[1]
        except:
            self.settings = []
        yield self.setup_listeners()
        yield self.initializeGUI()

    @inlineCallbacks
    def setup_listeners(self):
        ctx = yield self.PMT.context()
        yield self.PMT.signal__new_count(SIGNALID, context=ctx)
        yield self.PMT.addListener(listener=self.on_new_counts,
                                   source=None, ID=SIGNALID, context=ctx)

    @inlineCallbacks
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        self.shutter_widget = QCustomSwitchChannel('399/Oven/ProtectionBeam',
                                                   ('Open/Oven On', 'Closed/Oven Off'))
        self.shutter_widget.TTLswitch.toggled.connect(self.toggle)
        self.timer_widget = QCustomTimer('Loading Time', show_control=False)
        self.disc_widget = QCustomSpinBox('kcts/s',
                                          (0.0, 999.0))
        self.current_widget = QCustomSpinBox("Current ('A')", (0.0, 3.0))
        self.resistance_label = QtGui.QLabel('resistance: ')
        shell_font = 'MS Shell Dlg 2'
        self.resistance_label.setFont(QtGui.QFont(shell_font, pointSize=16))

        qBox = QtGui.QGroupBox('Discriminator')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)

        subLayout.addWidget(self.disc_widget)
        subLayout.addWidget(self.current_widget)

        self.current_widget.setStepSize(0.01)
        self.current_widget.spinLevel.setDecimals(2)
        self.current_widget.spinLevel.valueChanged.connect(self.current_changed)
        self.disc_widget.setStepSize(0.1)
        self.disc_widget.spinLevel.setDecimals(1)
        self.disc_widget.spinLevel.valueChanged.connect(self.disc_changed)

        if 'discriminator' in self.settings:
            value = yield self.reg.get('discriminator')
            self.disc_widget.spinLevel.setValue(value)

        if 'oven' in self.settings:
            value = yield self.reg.get('oven')
            self.current_widget.spinLevel.setValue(value)

        if '399 trapshutter' in self.settings:
            value = yield self.reg.get('399 trapshutter')
            value = bool(value)
            self.shutter_widget.TTLswitch.setChecked(value)
        else:
            self.shutter_widget.TTLswitch.setChecked(False)

        layout.addWidget(self.shutter_widget, 0, 0)
        layout.addWidget(qBox, 0, 1)
        layout.addWidget(self.timer_widget, 0, 2)
        layout.addWidget(self.resistance_label)
        self.setLayout(layout)

    @inlineCallbacks
    def on_new_counts(self, signal, pmt_value):
        switch_on = self.shutter_widget.TTLswitch.isChecked()
        disc_value = self.disc_widget.spinLevel.value()
        if (pmt_value >= disc_value) and switch_on:
            self.shutter_widget.TTLswitch.setChecked(False)
        if self.timer_widget.time >= 6000.0:
            self.shutter_widget.TTLswitch.setChecked(False)
        yield None

    @inlineCallbacks
    def toggle(self, value):
        yield self.changeState(value)
        if value:
            self.timer_widget.reset()
            self.timer_widget.start()
            self.oven.oven_output(True)
        else:
            self.oven.oven_output(False)
            self.timer_widget.stop()

    @inlineCallbacks
    def disc_changed(self, value):
        if 'discriminator' in self.settings:
            yield self.reg.set('discriminator', value)

    @inlineCallbacks
    def current_changed(self, value):
        yield self.oven.oven_current(self.U(value, 'A'))
        if 'oven' in self.settings:
            yield self.reg.set('oven', value)

    @inlineCallbacks
    def changeState(self, state):
        if '399 trapshutter' in self.settings:
            yield self.reg.set('399 trapshutter', state)
        if 'Protection Beam' in self.settings:
            yield self.reg.set('Protection Beam', state)
        yield self.TTL.ttl_output(9, state)
        yield self.TTL.ttl_output(10, state)

    @inlineCallbacks
    def measure(self):
        yield None
        #if self.kt:
            #current = yield self.kt.current(3)
            #voltage = yield self.kt.voltage(3)
            #output = yield self.kt.output(3)
            #color = (0, 0, 0)
            #if (current >= 0.0 and output == True):
            #    resistance = voltage['mV']/current['A']
            #    red = int(21.25 * resistance - 4760)
            #    green = int((-1*abs(red - 123) + 123)*0.1)
            #    blue = int(255 - red)
            #    color = (red, green, blue)
            #    #self.dv.add(self.timer_widget.time, resistance)
            #    resistance = '%.2f' % resistance
            #else :
            #    resistance = 'inf'
            #self.resistance_label.setText('R = ' + resistance + ' mOhm')
            #self.resistance_label.setStyleSheet('color: rgb' + str(color))

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
