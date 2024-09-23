from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui


# from common.lib.clients.qtui.q_custom_text_changing_button import \
#     TextChangingButton


class KeithleyClient(QtGui.QWidget):

    def __init__(self, reactor, parent=None):
        """initializes the GUI creates the reactor"""
        super(KeithleyClient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.connect()
        self.reactor = reactor

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection"""
        from labrad.wrappers import connectAsync
        from labrad.units import WithUnit as U

        self.U = U
        self.cxn = yield connectAsync(name="keithley client")
        self.server = self.cxn.keithley_2230g_server
        yield self.server.select_device(0)
        self.initializeGUI()

    def initializeGUI(self):
        layout = QtGui.QGridLayout()

        self.setWindowTitle("keithley Control")

        qBox = QtGui.QGroupBox("Keithley 2230G")
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)

        self.volt1widget = QCustomSpinBox((0, 30), suffix="V")
        self.volt2widget = QCustomSpinBox((0, 30), suffix="V")

        self.volt1widget.spin_level.valueChanged.connect(
            lambda value=self.volt1widget.spin_level.value(), chan=1: self.voltchanged(
                chan, value
            )
        )
        self.volt2widget.spin_level.valueChanged.connect(
            lambda value=self.volt2widget.spin_level.value(), chan=2: self.voltchanged(
                chan, value
            )
        )
        subLayout.addWidget(self.volt1widget, 1, 1)
        subLayout.addWidget(self.volt2widget, 1, 3)
        self.setLayout(layout)

    @inlineCallbacks
    def voltchanged(self, chan, value):
        value = self.U(value, "V")
        yield self.server.voltage(chan, value)

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor

    qt4reactor.install()
    from twisted.internet import reactor

    keithleyWidget = KeithleyClient(reactor)
    keithleyWidget.show()
    run = reactor.run()
