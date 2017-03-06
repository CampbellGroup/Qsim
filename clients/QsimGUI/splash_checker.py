from PyQt4 import QtGui, QtCore
import sys, time

class Form(QtGui.QWidget):
    pass

def setupfont():
    font = QtGui.QFont()
    font.setFamily('Lucida')
    font.setFixedPitch(True)
    font.setPointSize(20)
    return font

def generatesplash():
    pixmap = QtGui.QPixmap("/home/qsimexpcontrol/LabRAD/Qsim/clients/QsimGUI/zoo8withring.png")
    splash = QtGui.QSplashScreen(pixmap)
    font = setupfont()
    splash.setFont(font)
    splash.show()
    splash.showMessage('Checking LabRAD....\n', color = QtCore.Qt.white)
    cxn = checklabrad()
    time.sleep(0.5)
    if cxn:
        splash.showMessage('LabRAD Connected!\n', color = QtCore.Qt.green)
    else:
        splash.showMessage('LabRAD not running\n', color = QtCore.Qt.red)
	time.sleep(5)
	sys.exit("Labrad not running")
    time.sleep(0.5)
    splash.showMessage('Checking Node....\n', color = QtCore.Qt.white)
    node = checknode(cxn)
    time.sleep(0.5)
    if node:
        splash.showMessage('Node Connected!\n', color = QtCore.Qt.green)
	time.sleep(0.5)
    else:
        splash.showMessage('Node not running\n', color = QtCore.Qt.red)
	time.sleep(5)
	sys.exit("Node not running")
    checknodeserver(node, splash)
    time.sleep(0.5)
    return splash

def checklabrad():
    try:
        import labrad
    	cxn = labrad.connect(name='gui check', password='lab')
        return cxn
    except:
        return None

def checknode(cxn):
    try:
        node = cxn.node_mj
        return node
    except:
        return None

def checknodeserver(node, splash):
    autostart = node.autostart_list()
    running = node.running_servers()
    runninglist = []
    for item in running:
	runninglist.append(item[0])
    for item in autostart:
        inlist = item in runninglist
        if inlist:
	     splash.showMessage(item + ' Server running\n', color = QtCore.Qt.green)
        else:
             splash.showMessage('Warning: \n' + item + " not running\n", color = QtCore.Qt.yellow)
	time.sleep(0.5)

if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    splash = generatesplash()
    form = Form()
    splash.finish(form)

