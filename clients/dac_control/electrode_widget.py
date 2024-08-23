#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Rod:

    def __init__(self, dac, voltage=0.0, shape="circle", saturation_voltage=7.0):
        self.dac = dac
        self.voltage = voltage
        self.shape = shape
        self._position = None
        self.saturation_voltage = saturation_voltage

    @property
    def color(self):
        r = 255 if self.voltage > 0 else 0
        g = 0
        b = 255 if self.voltage < 0 else 0
        a = min(int(255 * abs(self.voltage) / self.saturation_voltage), 255)

        return QColor(r, g, b, a)

    @property
    def position(self):
        return tuple(map(int, self._position))

    @position.setter
    def position(self, tup):
        self._position = tup


class ElectrodeIndicator(QWidget):

    def __init__(self):

        super(ElectrodeIndicator, self).__init__()
        self.init_ui()

    def init_ui(self):
        self.min_height = 300
        self.min_width = 200

        self.setMinimumSize(self.min_width, self.min_height)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

        self.rods = [Rod(dac=2, saturation_voltage=1.0),
                     Rod(dac=19, saturation_voltage=1.0),
                     Rod(dac=17, saturation_voltage=1.0),
                     Rod(dac=21, saturation_voltage=1.0),
                     Rod(dac=8, shape="roundedRect", saturation_voltage=100.0),
                     Rod(dac=10, shape="roundedRect", saturation_voltage=100.0), ]

        self.show()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_electrodes(qp)
        self.draw_values(qp)
        qp.end()

    def draw_electrodes(self, qp):
        self.rod_diameter = min(self.height(), self.width()) // 4
        self.edge_padding = 25
        self.ec_dimension = self.rod_diameter

        trap_dimension = min(self.height(), self.width()) - self.rod_diameter - 2 * self.edge_padding
        centering_padding = (self.width() / 2 - trap_dimension / 2 - self.rod_diameter / 2) \
            if self.width() > self.height() else self.edge_padding

        trap_left = 0 + centering_padding
        trap_right = trap_left + trap_dimension

        trap_top = 0 + self.edge_padding
        trap_bottom = trap_top + trap_dimension

        positions = [
            (trap_left, trap_top, self.rod_diameter, self.rod_diameter),
            (trap_right, trap_top, self.rod_diameter, self.rod_diameter),
            (trap_left, trap_bottom, self.rod_diameter, self.rod_diameter),
            (trap_right, trap_bottom, self.rod_diameter, self.rod_diameter),
            (self.edge_padding, (self.height() - self.ec_dimension) / 2,
             centering_padding - 2 * self.edge_padding, self.ec_dimension,),
            (self.width() - centering_padding + self.edge_padding, (self.height() - self.ec_dimension) / 2,
             centering_padding - 2 * self.edge_padding, self.ec_dimension,)
        ]

        for i in range(len(self.rods)):
            self.rods[i].position = positions[i]

        # Draw the shapes
        pen = QPen(Qt.lightGray, 2, Qt.PenStyle.SolidLine)
        qp.setPen(pen)
        for rod in self.rods:
            qp.setBrush(rod.color)
            path = QPainterPath()
            if rod.shape == "circle":
                path.addEllipse(QRectF(*rod.position))
            elif rod.shape == "roundedRect":
                path.addRoundedRect(QRectF(*rod.position), 10, 10)
            qp.drawPath(path)

        # draw the text
        pen = QPen(Qt.black, 1, Qt.PenStyle.SolidLine)
        qp.setPen(pen)
        for rod in self.rods:
            qp.drawText(QRectF(*rod.position),
                        Qt.AlignCenter,
                        str(round(rod.voltage, 4)))

    def draw_values(self, qp):
        pen = QPen(Qt.red, 2, Qt.PenStyle.SolidLine)
        qp.setPen(pen)

    def update_rod(self, dac_num, value):
        for rod in self.rods:
            if rod.dac == dac_num:
                rod.voltage = value
        self.repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    indicator = ElectrodeIndicator()
    indicator.show()
    app.exec_()
