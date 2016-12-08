from common.lib.clients.qtui.multiplexerchannel import QCustomWavemeterChannel
from common.lib.clients.qtui.multiplexerPID import QCustomPID
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton
from twisted.internet.defer import inlineCallbacks, returnValue
from common.lib.clients.qtui.switch import QCustomSwitchChannel
from PyQt4 import QtGui
import socket
import os
import time


class rear_port_client(QtGui.QWidget):

    def __init__(self, reactor, parent=None):
        """initializels the GUI creates the reactor
            and empty dictionary for channel widgets to
            be stored for iteration. also grabs chan info
            from multiplexer_config
        """
        super(rear_port_client, self).__init__()
        self.password = os.environ['LABRADPASSWORD']
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.name = socket.gethostname() + ' Rear Port Client'
        self.continuous = False
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the wavemeter computer and
        connects incoming signals to relavent functions

        """

        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('10.97.112.2',
                                      name=self.name,
                                      password=self.password)
        self.server = yield self.cxn.multiplexerserver

        self.initializeGUI()

    def initializeGUI(self):

        layout = QtGui.QGridLayout()
        self.setWindowTitle('Wavemeter Rear Port')

        qBox = QtGui.QGroupBox('Rear Port')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0)

        wmChannel = 9
        hint = '811.291490'
        dacPort = 'rear'
        self.widget = QCustomWavemeterChannel('369 Rear Port', wmChannel,
                                         dacPort, hint, True, False)
        from common.lib.clients.Multiplexer import RGBconverter as RGB
        RGB = RGB.RGBconverter()
        color = int(2.998e8/(float(hint)*1e3))
        color = RGB.wav2RGB(color)
        color = tuple(color)
        self.continuous_switch = QCustomSwitchChannel('Continuous Measure')
        self.continuous_switch.TTLswitch.toggled.connect(self.toggle)
        self.widget.spinFreq.setValue(float(hint))
        self.widget.currentfrequency.setStyleSheet('color: rgb' + str(color))
        subLayout.addWidget(self.widget, 0, 0, 1, 3)
        subLayout.addWidget(self.continuous_switch, 1, 0, 1, 1)
        self.setLayout(layout)
        from twisted.internet.reactor import callLater
        self.update_value()

    @inlineCallbacks
    def update_value(self):

        self.reactor.callLater(1, self.update_value)
        if not self.widget.measSwitch.isChecked():
            self.widget.currentfrequency.setText('Not Measured')
            return

        if self.continuous:
            switchmode = yield self.server.get_switcher_mode()
            if switchmode:
                yield self.server.set_switcher_mode(False)
                yield self.server.set_active_channel(9)

            yield self.server.set_active_channel(9)
            freq = yield self.server.get_frequency(9)
            self.set_freq(freq)
            return

        yield self.server.set_switcher_mode(False)
        yield self.server.set_active_channel(9)
        time.sleep(0.3)
        freq = yield self.server.get_frequency(9)
        self.set_freq(freq)
        yield self.server.set_active_channel(1)
        yield self.server.set_switcher_mode(True)

    def set_freq(self, freq):
        if freq == -3.0:
            self.widget.currentfrequency.setText('Under Exposed')
        elif freq == -4.0:
            self.widget.currentfrequency.setText('Over Exposed')
        else:
            self.widget.currentfrequency.setText(str(freq)[0:10])

    def toggle(self, state):

        self.continuous = state


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    rearPortWidget = rear_port_client(reactor)
    rearPortWidget.show()
    reactor.run()
