#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
import numpy as np
from PyQt4 import QtGui, QtCore


class ElectrodeWedge():
    """
    Represents two opposite electrodes on the top and bottom of the trap.

    Stores values for the ElectrodeIndicator class.
    """
    def __init__(self, starting_angle, top_voltage=0.0, bottom_voltage=0.0,
                 max_voltage=15.):
        """
        starting_angle: describes how the electrode is drawn in degrees.
        """
        self.starting_angle = starting_angle
        # Voltage attributes are used to set the wedge color.
        self.top_voltage = top_voltage
        self.bottom_voltage = bottom_voltage
        self.max_voltage = max_voltage
        self.change_color(0.0)

    def change_color(self, voltage):
        """
        Converts a voltage to a color going from blue to red (neg. to pos.)
        """
        brightness = 150
        darkness = 255 - brightness

        red = int(brightness + voltage*darkness/self.max_voltage)
        green = int(brightness - abs(voltage*darkness/self.max_voltage))
        blue = int(brightness - voltage*darkness/self.max_voltage)

        self.color = QtGui.QColor(red, green, blue, 127)


class ElectrodeIndicator(QtGui.QWidget):
    """
    self.update_octant is the only function that should be called by the end
    user.
    """

    def __init__(self, min_voltage, max_voltage):
        super(ElectrodeIndicator, self).__init__()
        self.minvalue = min_voltage
        self.maxvalue = max_voltage
        self.init_GUI()

    def init_GUI(self):

        self.setGeometry(200, 200, 600, 600)

        quad1 = ElectrodeWedge(starting_angle=0.0)
        quad2 = ElectrodeWedge(starting_angle=90.0)
        quad3 = ElectrodeWedge(starting_angle=180.0)
        quad4 = ElectrodeWedge(starting_angle=270.0)

        self.quads = [quad1, quad2, quad3, quad4]
        self.top_electrodes = ['DAC 0', 'DAC 1', 'DAC 2', 'DAC 3']
        self.bottom_electrodes = ['DAC 4', 'DAC 5', 'DAC 6', 'DAC 7']

        self.setWindowTitle('Electrode Indicator')
        self.show()

    def paintEvent(self, exception):
        """
        Redraws the electrode circle when a value is change or the size
        of the window is changed, for example.
        """
        qp = QtGui.QPainter()
        qp.begin(self)
        self._draw_wedges(qp)
        qp.end()

    def _draw_wedges(self, qp):

        # Makes the circle 75% of the window size.
        framewidth = self.frameGeometry().width()
        frameheight = self.frameGeometry().height()
        trapdim = .75*min(framewidth, frameheight)
        center = QtCore.QPoint(framewidth/2, frameheight/2)

        # Bounding box for the wedge.
        xcoord = (framewidth - trapdim)/2
        ycoord = (frameheight - trapdim)/2

        pen = QtGui.QPen(QtCore.Qt.black, 1, QtCore.Qt.SolidLine)
        qp.setPen(pen)

        signs = [(1, -2), (-2, -2), (-2, 1), (1, 1)]
        position_scaling = 8
        bottom_offset = 20
        for i in range(4):
            x_top_position = signs[i][0]*trapdim/position_scaling
            y_top_position = signs[i][1]*trapdim/position_scaling
            top_position = center + QtCore.QPoint(x_top_position, y_top_position)
            qp.drawText(top_position, str(self.quads[i].top_voltage))

            x_bot_position = signs[i][0]*trapdim/position_scaling + bottom_offset
            y_bot_position = signs[i][1]*trapdim/position_scaling + bottom_offset
            bot_position = center + QtCore.QPoint(x_bot_position, y_bot_position)
            qp.drawText(bot_position, str(self.quads[i].bottom_voltage))

        # Pen is changed to grey for the edges and wedge lines.
        pen = QtGui.QPen(QtCore.Qt.gray, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)

        for quad in self.quads:
            qp.setBrush(quad.color)
            path = QtGui.QPainterPath(center)
            path.arcTo(xcoord, ycoord, trapdim, trapdim, quad.starting_angle, 90.0)
            path.lineTo(center)
            qp.drawPath(path)

    def update_octant(self, electrode):
        """
        Set the mean values of the wedges and they will correspondingly change
        color.

        Parameters
        ----------
        electrode: Electrode instance.
        """
        if electrode.name in self.top_electrodes:
            number = electrode.number
            self.quads[number].top_voltage = electrode.voltage
            value2 = self.quads[number].bottom_voltage
            self.quads[number].change_color(np.mean([electrode.voltage, value2]))

        if electrode.name in self.bottom_electrodes:
            number = electrode.number - 4
            self.quads[number].bottom_voltage = electrode.voltage
            value2 = self.quads[number].top_voltage
            self.quads[number].change_color(np.mean([electrode.voltage, value2]))
        self.repaint()

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    icon = ElectrodeIndicator([-5.0, 5.0])
    icon.show()
    app.exec_()
