#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore, QtWebKit, QtNetwork
from twisted.internet.defer import inlineCallbacks, returnValue
import socket

SIGNALID1 = 445567

cookieJar = QtNetwork.QNetworkCookieJar()

networkAccessManager = QtNetwork.QNetworkAccessManager()
networkAccessManager.setCookieJar(cookieJar)

class myWebView(QtWebKit.QWebView):
    _windows = set()

    def __init__(self, parent=None):
        super(myWebView, self).__init__(parent)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanAccessClipboard, True)
        self.page().setNetworkAccessManager(networkAccessManager)

        url = url = QtCore.QUrl("http://10.97.112.16/control.htm")
        url.setUserName("main")
        url.setPassword("main")
        self.load(url)

    @classmethod
    def _removeWindow(cls, window):
        if window in cls._windows:
            cls._windows.remove(window)

    @classmethod
    def newWindow(cls):
        window = cls()
        cls._windows.add(window)
        return window

    def closeEvent(self, event):
        self._removeWindow(self)
        event.accept()

    def createWindow(self, webWindowType):
        window = self.newWindow()
        if webWindowType == QtWebKit.QWebPage.WebModalDialog:
            window.setWindowModality(QtCore.Qt.ApplicationModal)

        window.show()

        return window

class M2Window(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(M2Window, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to the wavemeter computer and
        connects incoming signals to relavent functions
        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('10.97.112.2', name = socket.gethostname() + ' M2 Client', password='lab')
        self.server = yield self.cxn.multiplexerserver
        yield self.server.signal__frequency_changed(SIGNALID1)
        yield self.server.addListener(listener = self.updateFrequency, source = None, ID = SIGNALID1)

        self.initializeGUI()

    def initializeGUI(self):

        layout = QtGui.QGridLayout()
        self.setWindowTitle('Ti-Saph Control')
        qBox = QtGui.QGroupBox('Wave Length and Lock settings')
        subLayout = QtGui.QGridLayout()
        qBox.setLayout(subLayout)
        layout.addWidget(qBox, 0, 0), returnValue
        self.centralwidget = QtGui.QWidget(self)
        self.webView = myWebView(self.centralwidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(30)
        self.title = QtGui.QLabel('M Squared Ti-Saph Laser')
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)
        self.wavelength = QtGui.QLabel('freq')
        self.wavelength.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=50))
        self.wavelength.setAlignment(QtCore.Qt.AlignCenter)
        self.wavelength.setStyleSheet('color: maroon')
        subLayout.addWidget(self.title, 0,0)
        subLayout.addWidget(self.webView, 1,0)
        subLayout.addWidget(self.wavelength, 2,0)

        self.setLayout(layout)

    def updateFrequency(self, c, signal):
        #self.wavelength.setText(signal)
        if signal[0] == 1:
            self.wavelength.setText(str(signal[1])[0:10])

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    M2WindowWidget = M2Window(reactor)
    M2WindowWidget.show()
    reactor.run()  # @UndefinedVariable

