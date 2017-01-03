from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtCore, QtGui, QtWebKit
import datetime
from common.lib.clients.connection import connection


class CustomWebView(QtWebKit.QWebView):
    '''
    This class must be seperate or javascript popup handling with createWindow
    doesnt work
    '''
    def __init__(self, parent=None):
        QtWebKit.QWebView.__init__(self, parent)

    def createWindow(self, webWindowType):
        return self


class analysis(QtGui.QWidget):

    def __init__(self, reactor, cxn=None):

        super(analysis, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.month = datetime.datetime.now().strftime("%B")
        self.year = datetime.datetime.now().strftime("%Y")
        self.cxn = cxn
        self.connect()

    @inlineCallbacks
    def connect(self):
        if self.cxn is None:
            self.cxn = connection("analysis")
            yield self.cxn.connect()
        self.initializeGUI()

    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        notebookwidget = self.makenotebookwidget()
        layout.addWidget(notebookwidget)
        self.setLayout(layout)

    def makenotebookwidget(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        self.notebook = CustomWebView()
        self.notebook.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        self.notebook.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True)
        self.notebook.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanAccessClipboard,
                                              True)
        self.notebook.load(QtCore.QUrl("http://localhost:8888/tree"))
        gridLayout.addWidget(self.notebook, 0, 0)
        widget.setLayout(gridLayout)
        return widget

    def closeEvent(self, x):
        self.reactor.stop()

if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    analysisWidget = analysis(reactor)
    analysisWidget.show()
    reactor.run()  # @UndefinedVariable
