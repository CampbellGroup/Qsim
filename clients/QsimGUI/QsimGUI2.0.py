from PyQt4 import QtGui
from twisted.internet.defer import inlineCallbacks, returnValue
import sys

class QSIM_GUI(QtGui.QMainWindow):
    def __init__(self, reactor, clipboard, parent=None):
        super(QSIM_GUI, self).__init__(parent)
        self.clipboard = clipboard
        self.reactor = reactor
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        from common.lib.clients.connection import connection
        cxn = connection(name = 'GUI Client')
        yield cxn.connect()
        self.create_layout(cxn)

    def create_layout(self, cxn):
        centralWidget = QtGui.QWidget()
        layout = QtGui.QHBoxLayout() 
        centralWidget.setLayout(layout)
        self.setCentralWidget(centralWidget)
        self.setWindowTitle('Qsim GUI')

    def closeEvent(self, x):
        self.reactor.stop()

if __name__=="__main__":
    a = QtGui.QApplication( sys.argv )
    clipboard = a.clipboard()
    import common.lib.clients.qt4reactor as qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    QsimGUI = QSIM_GUI(reactor, clipboard)
    QsimGUI.setWindowIcon(QtGui.QIcon('/home/qsimexpcontrol/Pictures/icons/6ions.jpg'))
    QsimGUI.setWindowTitle('Qsim GUI')
    QsimGUI.show()
    reactor.run()
