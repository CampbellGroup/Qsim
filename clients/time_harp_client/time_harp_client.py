from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui, QtCore
from common.lib.clients.qtui.switch import QCustomSwitchChannel


class TimeHarpClient(QtGui.QWidget):

    def __init__(self, reactor, cxn=None):
        super(TimeHarpClient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.cxn = cxn
        self.reactor = reactor
        from labrad.units import WithUnit as U
        self.U = U
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to timeharpserver
        """
        if self.cxn is None:
            self.cxn = connection(name='Time Harp Client')
            yield self.cxn.connect()
        self.server = yield self.cxn.get_server('timeharpserver')
        self.initialize_GUI()

    @inlineCallbacks
    def initialize_GUI(self):
        layout = QtGui.QGridLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(18)
        self.title = QtGui.QLabel('TimeHarp 260P')
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.title,               0, 0, 1, 3)
        self.setLayout(layout)


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    TimeHarpWidget = TimeHarpClient(reactor)
    TimeHarpWidget.show()
    run = reactor.run()
