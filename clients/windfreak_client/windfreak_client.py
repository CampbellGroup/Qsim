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
            self.gui.a.freqInput.setText(str(init_freq))
            self.gui.a.powerInput.setText(str(init_power))
            self.gui.a.chanNotif.setText(str(init_chan))
            self.gui.a.onoffNotif.setText(str(init_onoff))
        except Exception:
            pass

        self.gui.a.c2.clicked.connect(lambda: self.changeFreq(0, float(self.gui.a.freqInput.text())))
        self.gui.a.c3.clicked.connect(lambda: self.changePower(0, float(self.gui.a.powerInput.text())))
        self.gui.a.c4.clicked.connect(lambda: self.on(0))
        self.gui.a.c5.clicked.connect(lambda: self.off(0))

        self.gui.b.c2.clicked.connect(lambda: self.changeFreq(1, float(self.gui.b.freqInput.text())))
        self.gui.b.c3.clicked.connect(lambda: self.changePower(1, float(self.gui.b.powerInput.text())))
        self.gui.b.c4.clicked.connect(lambda: self.on(1))
        self.gui.b.c5.clicked.connect(lambda: self.off(1))

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


if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor

    client_inst = windfreak_client(reactor)
    client_inst.show()
    reactor.run()
