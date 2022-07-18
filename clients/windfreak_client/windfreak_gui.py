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

        freqText = QtGui.QLabel('Frequency (MHz): ')
        freqText.setFont(QtGui.QFont(shell_font, pointSize=16))
        freqText.setAlignment(QtCore.Qt.AlignCenter)

        self.freqInput = QtGui.QDoubleSpinBox(self)
        self.freqInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.freqInput.setRange(50, 14800)
        self.freqInput.setSingleStep(0.1)
        self.freqInput.setDecimals(3)
        # self.c1label =  QLabel()
        # self.c1label.setFont(QFont(shell_font, pointSize=16))
        # self.c1label.setAlignment(QtCore.Qt.AlignCenter)

        self.freq_conf_button = QtGui.QPushButton("confirm", self)
        self.freq_conf_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.freq_conf_label = QtGui.QLabel()
        self.freq_conf_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.freq_conf_label.setAlignment(QtCore.Qt.AlignCenter)

        powerText = QtGui.QLabel('Power (dBm): ')
        powerText.setFont(QtGui.QFont(shell_font, pointSize=16))
        powerText.setAlignment(QtCore.Qt.AlignCenter)

        self.powerInput = QtGui.QDoubleSpinBox(self)
        self.powerInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.powerInput.setRange(-80.0, 17.0)
        self.powerInput.setSingleStep(0.1)
        self.powerInput.setDecimals(1)
        # self.c1label =  QLabel()
        # self.c1label.setFont(QFont(shell_font, pointSize=16))
        # self.c1label.setAlignment(QtCore.Qt.AlignCenter)

        self.power_conf_button = QtGui.QPushButton("confirm", self)
        self.power_conf_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.power_conf_label = QtGui.QLabel()
        self.power_conf_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.power_conf_label.setAlignment(QtCore.Qt.AlignCenter)

        onoffText = QtGui.QLabel('RF On/Off: ')
        onoffText.setFont(QtGui.QFont(shell_font, pointSize=16))
        onoffText.setAlignment(QtCore.Qt.AlignCenter)

        self.onoffNotif = QtGui.QLabel('ON')
        self.onoffNotif.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.onoffNotif.setAlignment(QtCore.Qt.AlignCenter)

        self.on_button = QtGui.QPushButton("ON", self)
        self.on_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.on_label = QtGui.QLabel()
        self.on_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.on_label.setAlignment(QtCore.Qt.AlignCenter)

        self.off_button = QtGui.QPushButton("OFF", self)
        self.off_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.off_label = QtGui.QLabel()
        self.off_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.off_label.setAlignment(QtCore.Qt.AlignCenter)

        sweeponoffText = QtGui.QLabel('Continuous Sweep On/Off: ')
        sweeponoffText.setFont(QtGui.QFont(shell_font, pointSize=16))
        sweeponoffText.setAlignment(QtCore.Qt.AlignCenter)

        self.sweeponoffNotif = QtGui.QLabel('ON')
        self.sweeponoffNotif.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweeponoffNotif.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepon_button = QtGui.QPushButton("ON", self)
        self.sweepon_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepon_label = QtGui.QLabel()
        self.sweepon_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepon_label.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepoff_button = QtGui.QPushButton("OFF", self)
        self.sweepoff_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepoff_label = QtGui.QLabel()
        self.sweepoff_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepoff_label.setAlignment(QtCore.Qt.AlignCenter)

        chanText = QtGui.QLabel('Current Channel: ')
        chanText.setFont(QtGui.QFont(shell_font, pointSize=16))
        chanText.setAlignment(QtCore.Qt.AlignCenter)

        sweepLowLimText = QtGui.QLabel('Sweep Low Frequency (MHz): ')
        sweepLowLimText.setFont(QtGui.QFont(shell_font, pointSize=16))
        sweepLowLimText.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepLowLimInput = QtGui.QDoubleSpinBox(self)
        self.sweepLowLimInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepLowLimInput.setRange(50, 14800)
        self.sweepLowLimInput.setSingleStep(0.1)
        self.sweepLowLimInput.setDecimals(3)

        self.sweepLowLim_conf_button = QtGui.QPushButton("confirm", self)
        self.sweepLowLim_conf_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepLowLim_conf_label = QtGui.QLabel()
        self.sweepLowLim_conf_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepLowLim_conf_label.setAlignment(QtCore.Qt.AlignCenter)

        sweepHighLimText = QtGui.QLabel('Sweep High Frequency (MHz): ')
        sweepHighLimText.setFont(QtGui.QFont(shell_font, pointSize=16))
        sweepHighLimText.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepHighLimInput = QtGui.QDoubleSpinBox(self)
        self.sweepHighLimInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepHighLimInput.setRange(50, 14800)
        self.sweepHighLimInput.setSingleStep(0.1)
        self.sweepHighLimInput.setDecimals(3)

        self.sweepHighLim_conf_button = QtGui.QPushButton("confirm", self)
        self.sweepHighLim_conf_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepHighLim_conf_label = QtGui.QLabel()
        self.sweepHighLim_conf_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepHighLim_conf_label.setAlignment(QtCore.Qt.AlignCenter)

        sweepFreqStepText = QtGui.QLabel('Sweep Freq Step (MHz): ')
        sweepFreqStepText.setFont(QtGui.QFont(shell_font, pointSize=16))
        sweepFreqStepText.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepFreqStepInput = QtGui.QDoubleSpinBox(self)
        self.sweepFreqStepInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepFreqStepInput.setRange(0.001, 50)
        self.sweepFreqStepInput.setSingleStep(0.001)
        self.sweepFreqStepInput.setDecimals(3)

        self.sweepFreqStep_conf_button = QtGui.QPushButton("confirm", self)
        self.sweepFreqStep_conf_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepFreqStep_conf_label = QtGui.QLabel()
        self.sweepFreqStep_conf_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepFreqStep_conf_label.setAlignment(QtCore.Qt.AlignCenter)

        sweepTimeStepText = QtGui.QLabel('Sweep Time Step (ms): ')
        sweepTimeStepText.setFont(QtGui.QFont(shell_font, pointSize=16))
        sweepTimeStepText.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepTimeStepInput = QtGui.QDoubleSpinBox(self)
        self.sweepTimeStepInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepTimeStepInput.setRange(4, 10000)
        self.sweepTimeStepInput.setSingleStep(0.1)
        self.sweepTimeStepInput.setDecimals(3)

        self.sweepTimeStep_conf_button = QtGui.QPushButton("confirm", self)
        self.sweepTimeStep_conf_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepTimeStep_conf_label = QtGui.QLabel()
        self.sweepTimeStep_conf_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepTimeStep_conf_label.setAlignment(QtCore.Qt.AlignCenter)

        sweepLowPowerText = QtGui.QLabel('Sweep Low Power (dBm): ')
        sweepLowPowerText.setFont(QtGui.QFont(shell_font, pointSize=16))
        sweepLowPowerText.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepLowPowerInput = QtGui.QDoubleSpinBox(self)
        self.sweepLowPowerInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepLowPowerInput.setRange(-80.0, 17.0)
        self.sweepLowPowerInput.setSingleStep(0.1)
        self.sweepLowPowerInput.setDecimals(1)

        self.sweepLowPower_conf_button = QtGui.QPushButton("confirm", self)
        self.sweepLowPower_conf_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepLowPower_conf_label = QtGui.QLabel()
        self.sweepLowPower_conf_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepLowPower_conf_label.setAlignment(QtCore.Qt.AlignCenter)

        sweepHighPowerText = QtGui.QLabel('Sweep High Power (dBm): ')
        sweepHighPowerText.setFont(QtGui.QFont(shell_font, pointSize=16))
        sweepHighPowerText.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepHighPowerInput = QtGui.QDoubleSpinBox(self)
        self.sweepHighPowerInput.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepHighPowerInput.setRange(-80.0, 17.0)
        self.sweepHighPowerInput.setSingleStep(0.1)
        self.sweepHighPowerInput.setDecimals(1)

        self.sweepHighPower_conf_button = QtGui.QPushButton("confirm", self)
        self.sweepHighPower_conf_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepHighPower_conf_label = QtGui.QLabel()
        self.sweepHighPower_conf_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepHighPower_conf_label.setAlignment(QtCore.Qt.AlignCenter)

        sweepSingleonoffText = QtGui.QLabel('Sweep On/Off: ')
        sweepSingleonoffText.setFont(QtGui.QFont(shell_font, pointSize=16))
        sweepSingleonoffText.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepSingleonoffNotif = QtGui.QLabel('ON')
        self.sweepSingleonoffNotif.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepSingleonoffNotif.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepSingleon_button = QtGui.QPushButton("ON", self)
        self.sweepSingleon_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepSingleon_label = QtGui.QLabel()
        self.sweepSingleon_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepSingleon_label.setAlignment(QtCore.Qt.AlignCenter)

        self.sweepSingleoff_button = QtGui.QPushButton("OFF", self)
        self.sweepSingleoff_button.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepSingleoff_label = QtGui.QLabel()
        self.sweepSingleoff_label.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.sweepSingleoff_label.setAlignment(QtCore.Qt.AlignCenter)

        self.chanNotif = QtGui.QLabel('A')
        self.chanNotif.setFont(QtGui.QFont(shell_font, pointSize=16))
        self.chanNotif.setAlignment(QtCore.Qt.AlignCenter)

        # layout 1 row at a time

        layout.addWidget(title, 0, 2, 1, 2)

        layout.addWidget(freqText, 1, 0, 1, 2)
        layout.addWidget(self.freqInput, 2, 0, 1, 2)
        layout.addWidget(self.freq_conf_button, 2, 2, 1, 1)

        layout.addWidget(powerText, 1, 3, 1, 2)
        layout.addWidget(self.powerInput, 2, 3, 1, 2)
        layout.addWidget(self.power_conf_button, 2, 5, 1, 1)

        layout.addWidget(onoffText, 3, 0, 1, 2)
        layout.addWidget(self.onoffNotif, 4, 0, 1, 2)
        layout.addWidget(self.on_button, 5, 0, 1, 1)
        layout.addWidget(self.off_button, 5, 1, 1, 1)

        layout.addWidget(sweeponoffText, 3, 3, 1, 2)
        layout.addWidget(self.sweeponoffNotif, 4, 3, 1, 2)
        layout.addWidget(self.sweepon_button, 5, 3, 1, 1)
        layout.addWidget(self.sweepoff_button, 5, 4, 1, 1)

        layout.addWidget(sweepLowLimText, 6, 0, 1, 2)
        layout.addWidget(self.sweepLowLimInput, 7, 0, 1, 2)
        layout.addWidget(self.sweepLowLim_conf_button, 7, 2, 1, 1)

        layout.addWidget(sweepHighLimText, 6, 3, 1, 2)
        layout.addWidget(self.sweepHighLimInput, 7, 3, 1, 2)
        layout.addWidget(self.sweepHighLim_conf_button, 7, 5, 1, 1)

        layout.addWidget(sweepFreqStepText, 8, 0, 1, 2)
        layout.addWidget(self.sweepFreqStepInput, 9, 0, 1, 2)
        layout.addWidget(self.sweepFreqStep_conf_button, 9, 2, 1, 1)

        layout.addWidget(sweepTimeStepText, 8, 3, 1, 2)
        layout.addWidget(self.sweepTimeStepInput, 9, 3, 1, 2)
        layout.addWidget(self.sweepTimeStep_conf_button, 9, 5, 1, 1)

        layout.addWidget(sweepLowPowerText, 10, 0, 1, 2)
        layout.addWidget(self.sweepLowPowerInput, 11, 0, 1, 2)
        layout.addWidget(self.sweepLowPower_conf_button, 11, 2, 1, 1)

        layout.addWidget(sweepHighPowerText, 10, 3, 1, 2)
        layout.addWidget(self.sweepHighPowerInput, 11, 3, 1, 2)
        layout.addWidget(self.sweepHighPower_conf_button, 11, 5, 1, 1)

        layout.addWidget(sweepSingleonoffText, 12, 0, 1, 2)
        layout.addWidget(self.sweepSingleonoffNotif, 13, 0, 1, 2)
        layout.addWidget(self.sweepSingleon_button, 14, 0, 1, 1)
        layout.addWidget(self.sweepSingleoff_button, 14, 1, 1, 1)

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