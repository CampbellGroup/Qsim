"""
### BEGIN NODE INFO
[info]
name = ArduinoTTL
version = 1.0
description = 
instancename = ArduinoTTL
[startup]
cmdline = %PYTHON% %FILE%
timeout = 20
[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""


'''
Created on Nov 19, 2015
@author: anthonyransford
'''

from common.lib.servers.serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from labrad.server import Signal
from labrad import types as T
from twisted.internet.task import LoopingCall
from twisted.internet.defer import returnValue
from labrad.support import getNodeName
from labrad.units import WithUnit as U
import time

SERVERNAME = 'LaserQuantumPumpServer'
TIMEOUT = 1.0
BAUDRATE = 19200

class M2pump( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'M2pump'
    port = None
    serNode = getNodeName()
    timeout = T.Value(TIMEOUT,'s')
    
    
    @inlineCallbacks
    def initServer( self ):
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
	print port
        try:
            serStr = yield self.findSerial( self.serNode )
            self.initSerial( serStr, port, baudrate = BAUDRATE )
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else: raise
    
    @setting(1, 'Read Power')
    def readPower(self, c):
        yield self.ser.write_line('POWER?')
	time.sleep(0.1)
	power = yield self.ser.read()
	power = U(float(power[1:7]),'W')
	returnValue(power)

    @setting(2, 'Read Current')
    def readCurrent(self, c):
        yield self.ser.write_line('Current?')
	time.sleep(0.1)
	current = yield self.ser.read()
	current = float(current[1:6])
	returnValue(current)

    @setting(3, 'Status')
    def status(self, c):
        yield self.ser.write_line('STATUS?')
	time.sleep(0.1)
	status = yield self.ser.read()
	returnValue(status)

    @setting(4, 'Get Shutter Status')
    def shutterstatus(self, c):
        yield self.ser.write_line('SHUTTER?')
	time.sleep(0.1)
	shutter = yield self.ser.read()
	if shutter[0:14] == 'SHUTTER CLOSED':
		val = False
	elif shutter[0:12] == 'SHUTTER OPEN':
		val = True
	else: val = ''
	returnValue(val)

    @setting(5, 'Get Interlock Status')
    def interlockstatus(self, c):
        yield self.ser.write_line('INTERLOCK?')
	time.sleep(0.1)
	interlock = yield self.ser.read()
	if interlock[0:7] == 'ENABLED':
		lock = True
	elif interlock[0:8] == 'DISABLED':
		lock = False
	else: lock = ''
	returnValue(lock)

    @setting(6, 'Get laser Temp')
    def lasertempstatus(self, c):
        yield self.ser.write_line('HTEMP?')
	time.sleep(0.1)
	temp = yield self.ser.read()
	temp = U(float(temp[1:7]),'degC')
	returnValue(temp)

    @setting(7, 'Get FPU Temp')
    def FPUtempstatus(self, c):
        yield self.ser.write_line('PSUTEMP?')
	time.sleep(0.1)
	temp = yield self.ser.read()
	temp = U(float(temp[1:7]),'degC')
	returnValue(temp)

    @setting(8, 'Get Laser Serial Number')
    def serialnumber(self, c):
        yield self.ser.write_line('SERIAL?')
	time.sleep(0.1)
	serial = yield self.ser.read()
	serial = serial[0:4]
	returnValue(serial)

    @setting(9, 'Set Laser Power', value = ['v[W]'])
    def laserpower(self, c, value):
	if (7 >= value['W'] >= 0):
		value = round(value['W'],3)
		output = 'POWER=' + str(value)
		yield self.ser.write_line(output)
	else:
		yield None

    @setting(10, 'Laser On', value = 'b')
    def togglelaser(self, c, value):
	if value==True:
		yield self.ser.write_line('LASER=ON')
	elif value ==False:
		yield self.ser.write_line('LASER=OFF')
	else:
		yield None

    @setting(11, 'Shutter Open', value = 'b')
    def toggleshutter(self, c, value):
	if value==True:
		yield self.ser.write_line('SHUTTER OPEN')
	elif value ==False:
		yield self.ser.write_line('SHUTTER CLOSED')
	else:
		yield None

    
if __name__ == "__main__":
    from labrad import util
    util.runServer( M2pump() )