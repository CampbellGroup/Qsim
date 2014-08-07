#!/usr/bin/env python
#-*- coding:utf-8 -*-

from PyQt4 import QtGui, QtCore, QtWebKit, QtNetwork

cookieJar = QtNetwork.QNetworkCookieJar()

networkAccessManager = QtNetwork.QNetworkAccessManager()
networkAccessManager.setCookieJar(cookieJar)

class myWebView(QtWebKit.QWebView):
    _windows = set()

    def __init__(self, parent=None):
        super(myWebView, self).__init__(parent)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True)

        self.page().setNetworkAccessManager(networkAccessManager)

        self.load(QtCore.QUrl("http://10.97.112.16"))

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

class myWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(myWindow, self).__init__(parent)

        self.centralwidget = QtGui.QWidget(self)

        self.webView = myWebView(self.centralwidget)

        self.pushButton = QtGui.QPushButton(self.centralwidget)
        self.pushButton.setText("New Window")
        self.pushButton.clicked.connect(lambda: self.webView.createWindow(QtWebKit.QWebPage.WebBrowserWindow))

        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.addWidget(self.pushButton)
        self.verticalLayout.addWidget(self.webView)

        self.setCentralWidget(self.centralwidget)

if __name__ == "__main__":
    import  sys

    app  = QtGui.QApplication(sys.argv)
    main = myWindow()
    main.show()
    sys.exit(app.exec_())