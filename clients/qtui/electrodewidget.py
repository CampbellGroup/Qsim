#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
from itertools import product

class Wedge():
	
    def __init__(self, xcoord, ycoord, startingangle):

	self.xcoord = xcoord
	self.ycoord = ycoord
	self.startingangle = startingangle
	self.change_color(0.0)

    def change_color(self, voltage): 

        brightness = 150
        darkness = 255 - brightness

	R = int(brightness + voltage*darkness/15.)
	G = int(brightness - abs(voltage*darkness/15.))
        B = int(brightness - voltage*darkness/15.)

	self.color = QtGui.QColor(R, G, B, 127)

class ElectrodeIndicator(QtGui.QWidget):
    
    def __init__(self, limits):
        super(ElectrodeIndicator, self).__init__()
        self.init_UI()
	self.minvalue = limits[0]
	self.maxvalue = limits[1]
        
    def init_UI(self):      

        self.setGeometry(200, 200, 600, 600)

	quad1 = Wedge(None, None, 0.0)
	quad2 = Wedge(None, None, 90.0)
	quad3 = Wedge(None, None, 180.0)
	quad4 = Wedge(None, None, 270.0) 

	self.quads = [quad1, quad2, quad3, quad4]

        self.setWindowTitle('Electrode Indicator')
        self.show()

    def paintEvent(self, e):

        qp = QtGui.QPainter()
        qp.begin(self)
        self.draw_wedges(qp)
        self.draw_values(qp)
        qp.end()
        
    def draw_wedges(self, qp):
      
	framewidth = self.frameGeometry().width()
	frameheight = self.frameGeometry().height()
	trapdim = .75*min(framewidth, frameheight)
	center = QtCore.QPoint(framewidth/2, frameheight/2)
        pen = QtGui.QPen(QtCore.Qt.gray, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)
	
	xcoord = (framewidth - trapdim)/2
	ycoord = (frameheight - trapdim)/2

	for quad in self.quads:
	    qp.setBrush(quad.color)
	    path = QtGui.QPainterPath(center)
	    path.arcTo(xcoord, ycoord,
			trapdim, trapdim, quad.startingangle, 90.0)
	    path.lineTo(center)
	    qp.drawPath(path)
        
    def draw_values(self, qp):
        pen = QtGui.QPen(QtCore.Qt.red, 2, QtCore.Qt.SolidLine)
        qp.setPen(pen)

    def update_electrode(self, quadrant, value):
	if value >= self.maxvalue:
		value = self.maxvalue
	elif value <= self.minvalue:
		value = self.minvalue

	self.quads[quadrant - 1].change_color(value)
	self.repaint()
        
if __name__=="__main__":
    app = QtGui.QApplication(sys.argv)
    icon = ElectrodeIndicator([-5.0,5.0])
    icon.show()
    app.exec_()
