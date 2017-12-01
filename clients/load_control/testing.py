''' ps_test_QSound1.py
a simple template to test PySide widgets like QSound
PySide is the official LGPL-licensed version of PyQT
for free PySide Windows installers see:
http://developer.qt.nokia.com/wiki/PySide_Binaries_Windows
or
http://www.lfd.uci.edu/~gohlke/pythonlibs/
tested with Python33 and Pyside112  by vegaseat  29jul2013
'''
import time
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# replace [] with sys.argv for command line option
app = QApplication([])
# ----- start your widget test code ----
# pick a sound file (.wav only) you have
sound_file = "trap.wav"
QSound.play(sound_file)
# create a label to show file (allows for proper exit too)
label = QLabel(sound_file)
label.show()
# ---- end of widget test code -----
app.exec_()