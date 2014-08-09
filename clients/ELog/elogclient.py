from twisted.internet.defer import inlineCallbacks
from PyQt4 import QtGui
import datetime

class ELog(QtGui.QWidget):
    
    def __init__(self, reactor, parent = None):
            
        super(ELog, self).__init__() 
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.reactor = reactor
        self.connect() 
        
    @inlineCallbacks 
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name = "ELog")
        self.wiki = yield self.cxn.wiki_server
        self.initializeGUI()     

    def initializeGUI(self):      
        layout = QtGui.QGridLayout() 
        self.textbox = QtGui.QTextEdit(self)
        sendbutton = QtGui.QPushButton(self)
        sendbutton.setText('Send')
        sendbutton.clicked.connect(self.senddata)
        layout.addWidget(self.textbox, 0,0)
        layout.addWidget(sendbutton, 1, 0)
        
        self.setLayout(layout)
    
    @inlineCallbacks    
    def senddata(self, data):
        timetag = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        text = self.textbox.toPlainText()
        text = str(text)
        yield self.wiki.add_line_to_file(text)
        yield self.wiki.add_line_to_file( "##" + timetag)
        yield self.wiki.update_wiki()
        self.textbox.setPlainText('')
        
    def closeEvent(self, x):
        self.reactor.stop()
        
if __name__=="__main__":
    a = QtGui.QApplication( [] ) 
    from common.lib.clients import qt4reactor 
    qt4reactor.install()
    from twisted.internet import reactor
    ELogWidget = ELog(reactor) 
    ELogWidget.show()
    reactor.run()
        