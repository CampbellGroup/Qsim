#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Rod:

    def __init__(self, voltage=0.0):
        self.voltage = voltage
        self.color = compute_color(0.0)


def compute_color(voltage, saturation=7.0):
    saturation_voltage = saturation

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

        self.rod1 = Rod()
        self.rod2 = Rod()
        self.rod3 = Rod()
        self.rod4 = Rod()

        self.ec1 = Rod()
        self.ec2 = Rod()

        self.setWindowTitle('Electrode Indicator')
        self.show()

    def paintEvent(self, e):
        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_wedges(qp)
        self.draw_values(qp)
        qp.end()

    def draw_wedges(self, qp):
        frame_width = self.frameGeometry().width()
        frame_height = self.frameGeometry().height() - 40
        # center_top = QPoint(int(frame_width / 4), int(frame_height / 2))

        rod_diameter = min(frame_height, frame_width) / 4

        edge_padding = 25

        trap_dimension = min(frame_height, frame_width) - rod_diameter - 2 * edge_padding

        ec_dimension = rod_diameter

        centering_padding = (
                    frame_width / 2 - trap_dimension / 2 - rod_diameter / 2) if frame_width > frame_height else edge_padding

        trap_left = 0 + centering_padding
        trap_right = trap_left + trap_dimension

        trap_top = 0 + edge_padding
        trap_bottom = trap_top + trap_dimension

        rod_positions = {
            self.rod1: (trap_left, trap_top),
            self.rod2: (trap_right, trap_top),
            self.rod3: (trap_left, trap_bottom),
            self.rod4: (trap_right, trap_bottom)
        }

        # Draw the circles (and the triangles?)
        pen = QPen(Qt.lightGray, 2, Qt.PenStyle.SolidLine)
        qp.setPen(pen)
        for rod, pos in rod_positions.items():
            qp.setBrush(rod.color)
            path = QPainterPath()
            path.addEllipse(pos[0], pos[1], rod_diameter, rod_diameter)
            qp.drawPath(path)

        qp.setBrush(self.ec1.color)
        path = QPainterPath()
        path.addRoundedRect(edge_padding,
                            (frame_height - ec_dimension) / 2,
                            centering_padding - 2 * edge_padding,
                            ec_dimension,
                            10, 10)
        qp.drawPath(path)

        qp.setBrush(self.ec2.color)
        path = QPainterPath()
        path.addRoundedRect(frame_width - centering_padding + edge_padding,
                            (frame_height - ec_dimension) / 2,
                            centering_padding - 2 * edge_padding,
                            ec_dimension,
                            10, 10)
        qp.drawPath(path)

        # draw the text for the circles
        pen = QtGui.QPen(Qt.black, 1, Qt.PenStyle.SolidLine)
        qp.setPen(pen)
        for rod, pos in rod_positions.items():
            qp.drawText(QtCore.QPoint(int(pos[0]), int(pos[1])), str(round(rod.voltage, 4)))

        # for i in range(4):
        #     qp.drawText(center_top + QtCore.QPoint(int(signs[i][0] * trap_diameter / 8),
        #                                            int(signs[i][1] * trap_diameter / 8)),
        #                 str(round(self.rods[i].top_voltage, 4)))
        #     qp.drawText(center_bottom + QtCore.QPoint(int(signs[i][0] * trap_diameter / 8),
        #                                               int(signs[i][1] * trap_diameter / 8)),
        #                 str(round(self.rods[i].bottom_voltage, 4)))

    def draw_values(self, qp):
        pen = QtGui.QPen(Qt.red, 2, Qt.PenStyle.SolidLine)
        qp.setPen(pen)

    def update_octant(self, octant, value):
        if octant in [1, 2, 3, 4]:
            self.rods[octant - 1].top_voltage = value
            self.rods[octant - 1].top_color = compute_color(value)

        if octant in [5, 6, 7, 8]:
            self.rods[octant - 5].bottom_voltage = value
            self.rods[octant - 5].bottom_color = compute_color(value)

        self.repaint()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = ElectrodeIndicator([-5.0, 5.0])
    icon.show()
    app.exec_()
