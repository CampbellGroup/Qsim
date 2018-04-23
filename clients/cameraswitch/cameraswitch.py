from common.lib.clients.qtui.switch import QCustomSwitchChannel
from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui


class cameraswitch(QtGui.QWidget):

    def __init__(self, reactor, cxn=None):
        super(cameraswitch, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.cxn = cxn
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions

        """

        if self.cxn is None:
            self.cxn = connection(name="Camera Switch")
            yield self.cxn.connect()
        self.server = yield self.cxn.get_server('arduinottl')
        self.pmt = yield self.cxn.get_server('normalpmtflow')
        self.reg = yield self.cxn.get_server('registry')
        self.cam = yield self.cxn.get_server('andor_server')
        self.dv = yield self.cxn.get_server('data_vault')
        try:
            self.grapher = yield self.cxn.get_server('grapher')
        except:
            pass

        try:
            yield self.reg.cd(['', 'settings'])
            self.settings = yield self.reg.dir()
            self.settings = self.settings[1]
        except:
            self.settings = []
        self.initializeGUI()

    @inlineCallbacks
    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        widget = QCustomSwitchChannel('Camera/PMT Toggle', ('PMT', 'Camera'))
        take_image_widget = QtGui.QPushButton('Save Image')
        self.last_saved_label = QtGui.QLabel('file:')
        if 'cameraswitch' in self.settings:
            value = yield self.reg.get('cameraswitch')
            value = bool(value)
            widget.TTLswitch.setChecked(value)
        else:
            widget.TTLswitch.setChecked(False)

        widget.TTLswitch.toggled.connect(self.toggle)
        take_image_widget.clicked.connect(self.take_image)
        layout.addWidget(widget)
        layout.addWidget(take_image_widget)
        layout.addWidget(self.last_saved_label)
        self.setLayout(layout)

    @inlineCallbacks
    def toggle(self, state):
        '''
        Sends TTL pulse to switch camera and PMT
        '''
        if not state:
            self.pmt.set_mode('Normal')
        if state:
            self.pmt.set_mode('Differential')
        yield self.server.ttl_output(8, True)
        yield self.server.ttl_output(8, False)
        yield self.server.ttl_read(8)
        if 'cameraswitch' in self.settings:
            yield self.reg.set('cameraswitch', state)

    @inlineCallbacks
    def take_image(self, state):
        self.last_saved_label.setText('Taking Image ...')
        self.cam.abort_acquisition()
        image_region = yield self.cam.get_image_region()
        image_data = yield self.cam.get_most_recent_image()
        yield self.cam.start_live_display()
        yield self.dv.cd(['', 'quick_images'])
        dataset = yield self.dv.new('quick_images', [('', 'num')],
                                   [('', '', 'num')])
        yield self.dv.save_image(image_data, [image_region[5], image_region[3]], 1, dataset[1])
        self.last_saved_label.setText('file: ' + dataset[1])
        try:
            yield self.grapher.plot_image(image_data, [image_region[5], image_region[3]], 'Images',
                            str(dataset))
        except:
            pass

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    cameraswitchWidget = cameraswitch(reactor)
    cameraswitchWidget.show()
    reactor.run()
