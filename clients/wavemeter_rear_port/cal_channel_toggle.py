from common.lib.clients.qtui.switch import QCustomSwitchChannel
from twisted.internet.defer import inlineCallbacks
import os, socket
from PyQt4 import QtGui


class cal_toggle_switch(QtGui.QWidget):

    def __init__(self, reactor):
        super(cal_toggle_switch, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Rear Port Switcher'
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions

        """

        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('10.97.112.2',
                                      name=self.name,
                                      password=self.password)
        self.server = self.cxn.multiplexerserver
        self.switchmode = yield self.server.get_switcher_mode()
        if not self.switchmode:
            yield self.server.set_active_channel(9)

        self.initializeGUI()

    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        widget = QCustomSwitchChannel('Cal. Toggle', ('Cal', 'Switch Mode'))
        if not self.switchmode:
            widget.TTLswitch.setChecked(True)

        widget.TTLswitch.toggled.connect(self.toggle)
        layout.addWidget(widget)
        self.setLayout(layout)

    @inlineCallbacks
    def toggle(self, state):
        '''
        Sends switches cal vs switcher
        '''
        if state:
            yield self.server.set_switcher_mode(False)
            yield self.server.set_active_channel(9)
        else:
            yield self.server.set_active_channel(1) # this is because the wavemeter has a bug if switched when in cal mode
            yield self.server.set_switcher_mode(True)

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    cal_toggle_Widget = cal_toggle_switch(reactor)
    cal_toggle_Widget.show()
    reactor.run()