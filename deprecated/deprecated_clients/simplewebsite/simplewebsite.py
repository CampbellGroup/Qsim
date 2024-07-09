# -*- coding: utf-8 -*-
 #!/usr/bin/env python

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import *

class CustomWebView(QWebView):
    def __init__(self, parent = None):
        print("CustomWebView ctor")
        QWebView.__init__(self, parent)
    def createWindow(self, webWindowType):
        return self

app = QApplication(sys.argv)
web = CustomWebView()
#QWebView()
web.settings().setAttribute(QWebSettings.JavascriptEnabled, True)
web.settings().setAttribute(QWebSettings.JavascriptCanOpenWindows, True)
web.settings().setAttribute(QWebSettings.JavascriptCanAccessClipboard, True)
web.load(QUrl("http://10.97.112.16"))
web.show()
sys.exit(app.exec_())