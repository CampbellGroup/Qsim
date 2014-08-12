from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtCore, QtGui, QtWebKit
import datetime

class CustomWebView(QtWebKit.QWebView):
    def __init__(self, parent = None):
        QtWebKit.QWebView.__init__(self, parent)
    def createWindow(self, webWindowType):
        return self

class analysis(QtGui.QWidget):
    
    def __init__(self, reactor, parent = None):
            
        super(analysis, self).__init__() 
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.month = datetime.datetime.now().strftime("%B")
        self.year = datetime.datetime.now().strftime("%Y")
        self.connect() 
        
    @inlineCallbacks 
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name = "analysis")
        self.wiki = yield self.cxn.wiki_server
        self.initializeGUI()     

    def initializeGUI(self):      
        layout = QtGui.QGridLayout()
        self.tabwidget = QtGui.QTabWidget()        
        wikiwidget = self.makewikiwidget() 
        notebookwidget = self.makenotebookwidget()
        self.tabwidget.addTab(notebookwidget, "&Ipython Notebook")
        self.tabwidget.addTab(wikiwidget, "&Log Book")
        layout.addWidget(self.tabwidget)
        self.setLayout(layout)
    
    def makenotebookwidget(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        self.notebook = CustomWebView()
        self.notebook.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, True)
        self.notebook.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanOpenWindows, True)
        self.notebook.settings().setAttribute(QtWebKit.QWebSettings.JavascriptCanAccessClipboard, True)
        self.notebook.load(QtCore.QUrl("http://localhost:8888/notebooks/IPython-Notebook/"))
        gridLayout.addWidget(self.notebook, 0, 0)
        widget.setLayout(gridLayout)
        return widget
                
    def makewikiwidget(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        self.textbox = QtGui.QTextEdit(self)
        sendbutton = QtGui.QPushButton(self)
        sendbutton.setText('Send')
        sendbutton.clicked.connect(self.senddata)
        self.wikipage = QtWebKit.QWebView(self)
        self.wikipage.load(QtCore.QUrl("http://localhost:4567/" + self.month + '-' + self.year))
        gridLayout.addWidget(self.wikipage, 0,0, 5, 1)
        gridLayout.addWidget(self.textbox, 5, 0, 2,1)
        gridLayout.addWidget(sendbutton, 6, 0, 1, 1)
        widget.setLayout(gridLayout)
        return widget
        
    @inlineCallbacks    
    def senddata(self, data):
        timetag = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = self.textbox.toPlainText()
        text = str(text)
        yield self.wiki.add_line_to_file(text)
        yield self.wiki.add_line_to_file( "##" + timetag)
        yield self.wiki.update_wiki()
        self.textbox.setPlainText('')
        self.wikipage.load(QtCore.QUrl("http://localhost:4567/" + self.month + '-' + self.year))
        
    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__=="__main__":
    a = QtGui.QApplication( [] ) 
    from common.lib.clients import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    analysisWidget = analysis(reactor) 
    analysisWidget.show()
    reactor.run()
        