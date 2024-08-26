#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Wedge:

    def __init__(
        self, x_coord, y_coord, starting_angle, top_voltage=0.0, bottom_voltage=0.0
    ):
        self.top_voltage = top_voltage
        self.bottom_voltage = bottom_voltage
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.starting_angle = starting_angle
        self.top_color = compute_color(0.0)
        self.bottom_color = compute_color(0.0)


def compute_color(voltage):
    saturation_voltage = 7.0

    R = 255 if voltage > 0 else 0
    G = 0
    B = 255 if voltage < 0 else 0
    A = min(int(255 * abs(voltage) / saturation_voltage), 255)

    return QtGui.QColor(R, G, B, A)


class ElectrodeIndicator(QWidget):

    def __init__(self, limits):

        super(ElectrodeIndicator, self).__init__()
        self.init_UI()
        self.minvalue = limits[0]
        self.maxvalue = limits[1]

    def init_UI(self):
        self.setGeometry(160, 160, 400, 400)

        quad1 = Wedge(None, None, 0.0)
        quad2 = Wedge(None, None, 90.0)
        quad3 = Wedge(None, None, 180.0)
        quad4 = Wedge(None, None, 270.0)

        self.quads = [quad1, quad2, quad3, quad4]

        self.setWindowTitle("Electrode Indicator")
        self.show()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_wedges(qp)
        self.draw_values(qp)
        qp.end()

    def draw_wedges(self, qp):
        frame_width = self.frameGeometry().width()
        frame_height = self.frameGeometry().height()
        trap_diameter = 0.9 * min(frame_height, frame_width / 2)
        center_top = QPoint(int(frame_width / 4), int(frame_height / 2))
        center_bottom = QPoint(int(3 * frame_width / 4), int(frame_height / 2))

        x_coord_top = frame_width / 4 - trap_diameter / 2
        y_coord_top = (frame_height - trap_diameter) / 2

        x_coord_bottom = 3 * frame_width / 4 - trap_diameter / 2
        y_coord_bottom = (frame_height - trap_diameter) / 2

        signs = [(1, -2), (-2, -2), (-2, 1), (1, 1)]

        pen = QPen(Qt.lightGray, 2, Qt.PenStyle.SolidLine)
        qp.setPen(pen)

        for quad in self.quads[:4]:
            qp.setBrush(quad.top_color)
            path = QPainterPath(center_top)
            path.arcTo(
                x_coord_top,
                y_coord_top,
                trap_diameter,
                trap_diameter,
                quad.starting_angle,
                90.0,
            )
            path.lineTo(center_top)
            qp.drawPath(path)

            qp.setBrush(quad.bottom_color)
            path = QPainterPath(center_bottom)
            path.arcTo(
                x_coord_bottom,
                y_coord_bottom,
                trap_diameter,
                trap_diameter,
                quad.starting_angle,
                90.0,
            )
            path.lineTo(center_bottom)
            qp.drawPath(path)

        pen = QtGui.QPen(Qt.black, 1, Qt.PenStyle.SolidLine)
        qp.setPen(pen)
        for i in range(4):
            qp.drawText(
                center_top
                + QtCore.QPoint(
                    int(signs[i][0] * trap_diameter / 8),
                    int(signs[i][1] * trap_diameter / 8),
                ),
                str(round(self.quads[i].top_voltage, 4)),
            )
            qp.drawText(
                center_bottom
                + QtCore.QPoint(
                    int(signs[i][0] * trap_diameter / 8),
                    int(signs[i][1] * trap_diameter / 8),
                ),
                str(round(self.quads[i].bottom_voltage, 4)),
            )

    def draw_values(self, qp):
        pen = QtGui.QPen(Qt.red, 2, Qt.PenStyle.SolidLine)
        qp.setPen(pen)

    def update_octant(self, octant, value):
        if octant in [1, 2, 3, 4]:
            self.quads[octant - 1].top_voltage = value
            self.quads[octant - 1].top_color = compute_color(value)

        if octant in [5, 6, 7, 8]:
            self.quads[octant - 5].bottom_voltage = value
            self.quads[octant - 5].bottom_color = compute_color(value)

        self.repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = ElectrodeIndicator([-5.0, 5.0])
    icon.show()
    app.exec_()
