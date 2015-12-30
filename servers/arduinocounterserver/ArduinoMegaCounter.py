"""
### BEGIN NODE INFO
[info]
name = Arduino Counter
version = 1.0
description = 
instancename = Arduino Counter

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""


'''
Created on May 17, 2014

@author: anthonyransford
'''

from common.lib.servers.serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from twisted.internet.defer import returnValue
from labrad.server import Signal
from labrad import types as T
from twisted.internet.task import LoopingCall
import time as time

SERVERNAME = 'Arduino Counter'
TIMEOUT = 1.0
BAUDRATE = 115200
UPDATEREADINGID = 142879

class ArduinoCounter( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'ArduinoCounter'
    port = None
    serNode = 'qsimexpcontrol'
    timeout = T.Value(TIMEOUT,'s')
    on = False
    currentreading = 0.0
    reactorlooptime = 0.1
    updatetime = T.Value(100, 's')
    
    updatereading = Signal(UPDATEREADINGID, 'signal: new count', 'v')
    
    @inlineCallbacks
    def initServer( self ):
        #looks for registry key pointing arduino to arduino port, regkey goes in Ports folder with key name regKey and key is string i.e. 'COM3'
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
        #opens port of serial device
        port = yield self.getPortFromReg( self.regKey )
        self.port = port
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
        self.saveFolder = ['','PMT Counts']
#            self.dataSetName = 'PMT Counts'
        self.on = False
        self.getCounts()
        yield self.connect_data_vault()

                    
    @inlineCallbacks
    def connect_data_vault(self):
        try:
            #connect to data vault and navigate to the directory boolean True to plot live
            self.dv = yield self.client.data_vault
            liveplot = True
            yield self.dv.cd(self.saveFolder, liveplot)    
            print 'Connected: Data Vault'
        except AttributeError:
            self.dv = None
            print 'Not Connected: Data Vault'
        self.newDataSet(self)        
            
    @inlineCallbacks
    def getCounts(self):
        if self.on:  
            #recursively loop with reactor (kind of a hack better way with reactor looping call?)
            #not sure if loop can even run this fast, but must be faster than arduino 100ms PMT average , seems to work though
            try:
                reading = yield self.ser.readline()
            except:
                reading = None
            yield self.ser.flushinput()
            #reads arduino serial line output
            if reading:        
            #plots reading to data vault
                reading = float(reading)
                rate = reading/100.0
                try:
                    yield self.dv.add(time.time() - self.start, rate)
                    self.currentreading = rate
                    self.updatereading(rate)
                except:
                    yield None
            else: yield None
        else: yield None
        yield reactor.callLater(self.reactorlooptime, self.getCounts)  # @UndefinedVariable
        
    @inlineCallbacks   
    def StopServer(self):
        yield self.ser.flushinput()
        
        
    @setting(1, "toggle counting", value = 'b')
    def toggleCounting(self,c,value):
        if value == True: 
            self.on = True
        else:
            self.on = False
            
    @setting(2, "New Data Set", returns = 's')
    def newDataSet(self, c):
        filename = yield self.dv.new('PMT COUNTS',[('t', 'num')], [('kilocounts/sec','','num')])
        window_name = ['PMT Counts']
        yield self.dv.add_parameter('Window', window_name)
        yield self.dv.add_parameter('plotLive', True)
        self.start = time.time()
        returnValue( filename[1] )
        
    @setting(3, "Get Current Counts", returns = 'v' )
    def getCurrentReading(self, c):
        yield None
        returnValue( self.currentreading )

    @setting(4, "Set Update Time", value = 'v[s]')
    def set_update_time(self, c, value):
        if value['s'] >= 60.0: value = T.Value(60.0, 's')
        if value['s'] <= 0.01: value = T.Value(0.01, 's')
        self.updatetime = value
        value = long(value)
        yield self.ser.write(str(value))
        self.reactorlooptime = self.updatetime['s']
    
if __name__ == "__main__":
    from labrad import util
    util.runServer( ArduinoCounter() )
