
from PyQt4 import QtGui, QtCore
import serial
import sys
import labrad
from labrad.units import WithUnit as U
import time
import labrad

class Intensity_lock_control(QtGui.QWidget):

    def __init__(self):
        super(Intensity_lock_control, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        port = '/dev/ttyACM0'
        self.arduino = serial.Serial(port, 9600, timeout=5)
        self.cxn = labrad.connect()
        self.pzt = self.cxn.piezo_server
        self.pzt.select_device(0)
        self.current_voltage = self.pzt.set_voltage(2)[1]
        self.connect()
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.main_loop)
        timer.start(1)

    def connect(self):
        """Creates an Asynchronous connection to Pulser and
        connects incoming signals to relavent functions
        """
        self.initializeGUI()
        self.main_loop()

    def initializeGUI(self):
        layout = QtGui.QGridLayout()
        self.lcdwidget = QtGui.QLCDNumber()
        self.lock = False
        self.lock_set = QtGui.QSpinBox()
        self.lock_set.setMaximum(5000)
        self.lock_set.setValue(100)
        self.lock_button = QtGui.QPushButton('Lock')
        self.lock_button.setCheckable(True)
        self.lock_button.clicked.connect(self.lock_pressed)
        layout.addWidget(self.lcdwidget)
        layout.addWidget(self.lock_button)
        layout.addWidget(self.lock_set)

        self.setLayout(layout)

    def main_loop(self):

        self.current_voltage = self.pzt.set_voltage(2)[1]
        i = 0
        self.arduino.flushInput()
        val = self.arduino.readline()[0:-2]
        for i in range(64):
            milli_volts = 0
            k = 0
            if val:
                milli_volts += 5*int(1000*int(val)/(2**10 - 1))
                k +=1 
            else:
                continue
        if k != 0:
            milli_volts = milli_volts/float(k)
            self.lcdwidget.display(milli_volts)
            error = int(self.lock_set.value()) - int(val)
            to_write = 0.0001*error + float(self.current_voltage)
            if ((0 < to_write < 50) and self.lock):
                self.pzt.set_voltage(2, U(to_write, 'V'))

    def lock_pressed(self, state):
        self.lock = state


if __name__ == "__main__":
    a = QtGui.QApplication(sys.argv)
    lockWidget = Intensity_lock_control()
    lockWidget.show()
    sys.exit(a.exec_())
