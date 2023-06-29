import sys
from PyQt4 import QtCore, QtGui
from common.lib.clients.qtui.switch import QCustomSwitchChannel
from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
import sys
from common.lib.clients.qtui.q_custom_text_changing_button import TextChangingButton


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
        self.font = QtGui.QFont('MS Shell Dlg 2', pointSize=16)

    def makeLayout(self):
        qBoxLayout = QtGui.QVBoxLayout()
        qBox = QtGui.QGroupBox(self.title)
        layout = QtGui.QGridLayout()

        self.freq_input = QCustomSpinBox('Frequency (MHz)', (53.0, 14800.0), parent=self)
        self.power_input = QCustomSpinBox('Power (dBm)', (-80.0, 17.0), parent=self)

        self.onoff_button = TextChangingButton('RF output', parent=self)

        self.sweep_low_freq_input = QCustomSpinBox('Sweep Low Freq (MHz)', (53.0, 14800.0), parent=self)
        self.sweep_high_freq_input = QCustomSpinBox('Sweep High Freq (MHz)', (53.0, 14800.0), parent=self)

        self.sweep_freq_step_input = QCustomSpinBox('Sweep Freq Step (MHz)', (0.001, 50.0), parent=self)
        self.sweep_time_step_input = QCustomSpinBox('Sweep Time Step (ms)', (4.0, 10000.0), parent=self)

        self.sweep_low_power_input = QCustomSpinBox('Sweep Low Power (dBm)', (-80.0, 17.0), parent=self)
        self.sweep_low_power_input.setDecimals(1)
        self.sweep_high_power_input = QCustomSpinBox('Sweep High Power (dBm)', (-80.0, 17.0), parent=self)
        self.sweep_high_power_input.setDecimals(1)

        self.sweep_onoff_button = TextChangingButton('Sweep', parent=self)
        self.sweep_single_onoff_button = TextChangingButton('Sweep Single', parent=self)

        # layout 1 row at a time
        layout.addWidget(self.freq_input, 1, 0, 1, 1)
        layout.addWidget(self.power_input, 1, 1, 1, 1)

        layout.addWidget(self.onoff_button, 2, 0, 1, 2)

        layout.addWidget(self.sweep_low_freq_input, 3, 0, 1, 1)
        layout.addWidget(self.sweep_high_freq_input, 3, 1, 1, 1)

        layout.addWidget(self.sweep_low_power_input, 4, 0, 1, 1)
        layout.addWidget(self.sweep_high_power_input, 4, 1, 1, 1)

        layout.addWidget(self.sweep_freq_step_input, 5, 0, 1, 1)
        layout.addWidget(self.sweep_time_step_input, 5, 1, 1, 1)

        layout.addWidget(self.sweep_onoff_button, 6, 0, 1, 1)
        layout.addWidget(self.sweep_single_onoff_button, 6, 1, 1, 1)

        layout.minimumSize()
        qBox.setLayout(layout)
        qBoxLayout.addWidget(qBox)

        self.setLayout(qBoxLayout)


class QCustomWindfreakGui(QtGui.QFrame):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setFrameStyle(0x0001 | 0x0030)
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.makeLayout()

    def makeLayout(self):
        layout = QtGui.QGridLayout()
        qBox = QtGui.QGroupBox('Windfreak SynthHD')
        sublayout = QtGui.QHBoxLayout()
        self.a = QCustomWindfreakSubGui(title="Channel A")
        self.b = QCustomWindfreakSubGui(title="Channel B")
        sublayout.addWidget(self.a)
        sublayout.addWidget(self.b)
        qBox.setLayout(sublayout)
        layout.addWidget(qBox, 0, 0)

        layout.minimumSize()

        self.setLayout(layout)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = QCustomWindfreakGui()
    icon.show()
    app.exec_()
