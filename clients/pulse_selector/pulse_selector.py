import sys
from PyQt4 import QtGui
from common.lib.clients.qtui.q_custom_text_changing_button import \
    TextChangingButton


class QCustomPulsePlotter(QtGui.QFrame):
    def __init__(self, title = 'Pulse Plotter', parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout(title)

    def makeLayout(self, title):
        pulse_list = ['pulse 1', 'pulse 2','pulse 3','pulse 4',]
        layout = QtGui.QGridLayout()
        combo = QtGui.QComboBox()
        for sequence in pulse_list:
            combo.addItem(sequence)
        title = QtGui.QLabel(title)
        title.setFont(QtGui.QFont('MS Shell Dlg 2',pointSize=16))
        layout.addWidget(title, 0,0,1,3)
        layout.addWidget(combo, 1,0, 2,1)
        self.setLayout(layout)


if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomPulsePlotter()
    icon.show()
    app.exec_()