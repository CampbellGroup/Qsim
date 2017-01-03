"""
### BEGIN NODE INFO
[info]
name = M2pump
version = 1.0
description = 
instancename = M2Pump
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

UPDATECURR = 120377
UPDATEPOW = 118377
UPDATETMP = 156472

from common.lib.servers.serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from labrad.server import Signal
from labrad import types as T
from twisted.internet.task import LoopingCall
from twisted.internet.defer import returnValue
from labrad.support import getNodeName
from labrad.units import WithUnit as U
from labrad.util import wakeupCall

SERVERNAME = 'M2pump'
TIMEOUT = 1.0
BAUDRATE = 19200

class M2pump( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'M2pump'
    port = None
    serNode = getNodeName()
    timeout = T.Value(TIMEOUT,'s')
    temperature = None
    power = None
    current = None

    currentchanged = Signal(UPDATECURR, 'signal: current changed', 'v')
    powerchanged = Signal(UPDATEPOW, 'signal: power changed', 'v')
    temperaturechanged = Signal(UPDATETMP, 'signal: temp changed', 'v')
    
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
        self.measurePump()
    
    @setting(1, 'Read Power')
    def readPower(self, c):
        yield None
        returnValue(self.power)
 
    @inlineCallbacks
    def _readPower(self):
        yield self.ser.write_line('POWER?')
        power = yield self.ser.read_line()
        if power >=3:	
            self.power = U(float(power[0:-1]),'W')
        else:
            print 'bad data'
 
    @setting(2, "Read Current", returns = 'v')
    def readCurrent(self, c):
        yield None
        returnValue(self.current)
 
    @inlineCallbacks
    def _readCurrent(self):
        yield self.ser.write_line('Current?')
        current = yield self.ser.read_line()
        if len(current) >= 3:
            self.current = float(current[0:-3])	
        else:
            print 'bad data'
 
 
    @setting(3, 'Status')
    def status(self, c):
        yield self.ser.write_line('STATUS?')
        status = yield self.ser.read_line()
        returnValue(status)
 
    @setting(4, 'Get Shutter Status')
    def shutterstatus(self, c):
        yield self.ser.write_line('SHUTTER?')
        shutter = yield self.ser.read_line()
        if shutter[0:14] == 'SHUTTER CLOSED':
            val = False9
        elif shutter[0:12] == 'SHUTTER OPEN':
            val = True
        else: val = ''
        returnValue(val)
 
    @setting(5, 'Get Interlock Status')
    def interlockstatus(self, c):
        yield self.ser.write_line('INTERLOCK?')
        interlock = yield self.ser.read_line()
        if interlock[0:7] == 'ENABLED':
            lock = True
        elif interlock[0:8] == 'DISABLED':
            lock = False
        else: lock = ''
        returnValue(lock)
 
    @setting(6, 'Get laser Temp')
    def lasertempstatus(self, c):
        yield None
        returnValue(self.temperature)
 
    @inlineCallbacks
    def _readTemperature(self):
        yield self.ser.write_line('HTEMP?')
        temp = yield self.ser.read_line()
        if len(temp) >= 2:
            self.temperature = U(float(temp[0:-1]),'degC')
        else:
            print 'bad data'
 
    @setting(7, 'Get FPU Temp')
    def FPUtempstatus(self, c):
        yield self.ser.write_line('PSUTEMP?')
        temp = yield self.ser.read()
        #temp = U(float(temp[1:2]),'degC')
        returnValue(temp)
 
    @setting(8, 'Get Laser Serial Number')
    def serialnumber(self, c):
        yield self.ser.write_line('SERIAL?')
        serial = yield self.ser.read()
        serial = serial[0:4]
        returnValue(serial)
 
    @setting(9, 'Set Laser Power', value = ['v[W]'])
    def laserpower(self, c, value):
        if (7 >= value['W'] >= 0):
            value = round(value['W'],3)
            output = 'POWER=' + str(value)
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

    @inlineCallbacks
    def measurePump(self):
        reactor.callLater(.1, self.measurePump)
        yield self._readPower()
        yield self._readCurrent()
        yield self._readTemperature()
        self.currentchanged(self.current)
        self.powerchanged(self.power) 
        self.temperaturechanged(self.temperature)
   
if __name__ == "__main__":
    from labrad import util
    util.runServer( M2pump() )
