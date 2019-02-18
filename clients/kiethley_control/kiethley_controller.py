from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton


class kiethleyclient(QtGui.QWidget):

    def __init__(self, reactor, parent = None):
        """initializels the GUI creates the reactor
        """
        super(kiethleyclient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.connect()
        self.reactor = reactor

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection
        """
        from labrad.wrappers import connectAsync
        from labrad.units import WithUnit as U
        self.U = U
        self.cxn = yield connectAsync(name = "kiethley client")
        self.server = self.cxn.keithley_2230g_server
        yield self.server.select_device(0)
        self.initializeGUI()

    def initializeGUI(self):

        layout = QtGui.QGridLayout()

        self.setWindowTitle('kiethley Control')

        qBox = QtGui.QGroupBox('Kiethley 2230G')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)



        self.volt1widget = QCustomSpinBox('Amplitude (Vpp)', (0, 30))
        self.volt2widget = QCustomSpinBox('Amplitude (Vpp)', (0, 30))

        self.volt1widget.spinLevel.valueChanged.connect(lambda value = self.volt1widget.spinLevel.value(), chan = 1 : self.voltchanged(chan, value))
        self.volt2widget.spinLevel.valueChanged.connect(lambda value = self.volt2widget.spinLevel.value(), chan = 2 : self.voltchanged(chan, value))
        subLayout.addWidget(self.volt1widget, 1,1)
        subLayout.addWidget(self.volt2widget, 1,3)
        self.setLayout(layout)

    @inlineCallbacks
    def voltchanged(self, chan, value):
        value = self.U(value, 'V')
        yield self.server.voltage(chan, value)


    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    kiethleyWidget = kiethleyclient(reactor)
    kiethleyWidget.show()
    run = reactor.run()
