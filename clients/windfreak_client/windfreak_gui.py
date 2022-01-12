import sys
from PyQt4 import QtCore, QtGui
import sys
# from common.lib.clients.qtui.q_custom_text_changing_button import \
#     TextChangingButton


class StretchedLabel(QtGui.QLabel):
    def __init__(self, *args, **kwargs):
        QtGui.QLabel.__init__(self, *args, **kwargs)
        self.setMinimumSize(QtCore.QSize(500, 300))

    def resizeEvent(self, evt):
        font = self.font()
        font.setPixelSize(self.width() * 0.14 - 14)
        self.setFont(font)


class QCustomWindfreakSubGui(QtGui.QFrame):
    def __init__(self, parent=None, title="Windfreak"):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.title = title
        self.makeLayout()

    def action(self, button1, button2):
        """
    Create the effect of selected button1
    and unselect button2 or vice versa.
    """

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        shell_font = 'MS Shell Dlg 2'
        title = QtGui.QLabel(self.title)
        title.setFont(QtGui.QFont(shell_font, pointSize=16))
        title.setAlignment(QtCore.Qt.AlignCenter)

        freqText = QtGui.QLabel('Frequency: ')
        freqText.setFont(QtGui.QFont(shell_font, pointSize=16))
        freqText.setAlignment(QtCore.Qt.AlignCenter)

        self.freqInput = QtGui.QLineEdit(self)
        self.freqInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        # self.c1label =  QLabel()
        # self.c1label.setFont(QFont(shell_font, pointSize=16))
        # self.c1label.setAlignment(QtCore.Qt.AlignCenter)

        self.c2 = QtGui.QPushButton("confirm", self)
        self.c2.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c2label = QtGui.QLabel()
        self.c2label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c2label.setAlignment(QtCore.Qt.AlignCenter)

        powerText = QtGui.QLabel('Power: ')
        powerText.setFont(QtGui.QFont(shell_font, pointSize=16))
        powerText.setAlignment(QtCore.Qt.AlignCenter)

        self.powerInput = QtGui.QLineEdit(self)
        self.powerInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        # self.c1label =  QLabel()
        # self.c1label.setFont(QFont(shell_font, pointSize=16))
        # self.c1label.setAlignment(QtCore.Qt.AlignCenter)

        self.c3 = QtGui.QPushButton("confirm", self)
        self.c3.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c3label = QtGui.QLabel()
        self.c3label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c3label.setAlignment(QtCore.Qt.AlignCenter)

        onoffText = QtGui.QLabel('RF On/Off: ')
        onoffText.setFont(QtGui.QFont(shell_font, pointSize=16))
        onoffText.setAlignment(QtCore.Qt.AlignCenter)

        self.onoffNotif = QtGui.QLabel('ON')
        self.onoffNotif.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.onoffNotif.setAlignment(QtCore.Qt.AlignCenter)

        self.c4 = QtGui.QPushButton("ON", self)
        self.c4.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c4label = QtGui.QLabel()
        self.c4label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c4label.setAlignment(QtCore.Qt.AlignCenter)

        self.c5 = QtGui.QPushButton("OFF", self)
        self.c5.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c5label = QtGui.QLabel()
        self.c5label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.c5label.setAlignment(QtCore.Qt.AlignCenter)

        chanText = QtGui.QLabel('Current Channel: ')
        chanText.setFont(QtGui.QFont(shell_font, pointSize=16))
        chanText.setAlignment(QtCore.Qt.AlignCenter)

        self.chanNotif = QtGui.QLabel('A')
        self.chanNotif.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.chanNotif.setAlignment(QtCore.Qt.AlignCenter)

        # layout 1 row at a time

        layout.addWidget(title, 0, 2, 1, 2)

        layout.addWidget(freqText, 1, 0, 1, 2)
        layout.addWidget(self.freqInput, 2, 0, 1, 2)
        layout.addWidget(self.c2, 2, 2, 1, 1)

        layout.addWidget(powerText, 1, 3, 1, 2)
        layout.addWidget(self.powerInput, 2, 3, 1, 2)
        layout.addWidget(self.c3, 2, 5, 1, 1)

        layout.addWidget(onoffText, 3, 0, 1, 2)
        layout.addWidget(self.onoffNotif, 4, 0, 1, 2)
        layout.addWidget(self.c4, 5, 0, 1, 1)
        layout.addWidget(self.c5, 5, 1, 1, 1)

        layout.minimumSize()

        self.setLayout(layout)

class QCustomWindfreakGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()

        self.a = QCustomWindfreakSubGui(title="Channel A")
        self.b = QCustomWindfreakSubGui(title="Channel B")
        layout.addWidget(self.a, 0, 0)
        layout.addWidget(self.b, 0, 1)

        layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomWindfreakGui()
    icon.show()
    app.exec_()