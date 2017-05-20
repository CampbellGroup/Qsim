from common.lib.clients.qtui.switch import QCustomSwitchChannel
from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui
import socket
import os


class wm_dac_control(QtGui.QWidget):

    def __init__(self, reactor):
        super(wm_dac_control, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Single WM Lock Server'
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
        self.initializeGUI()

    def initializeGUI(self):
        layout = QtGui.QGridLayout()

        control = QCustomSpinBox("DC value ('V')", (-5.0, 5.0))
        control.setStepSize(0.0001)
        control.spinLevel.setDecimals(4)
        control.spinLevel.valueChanged.connect(self.set_dac)
        layout.addWidget(control)
        self.setLayout(layout)

    @inlineCallbacks
    def set_dac(self, value):
        yield self.server.set_dac_voltage(3, value)

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    Widget = wm_dac_control(reactor)
    Widget.show()
    reactor.run()
