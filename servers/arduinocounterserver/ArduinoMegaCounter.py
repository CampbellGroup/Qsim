"""
### BEGIN NODE INFO
[info]
name = ArduinoMegaFreqCounter
version = 1.0
description = 
instancename = ArduinoMegaFreqCounter

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

from serialdeviceserver import SerialDeviceServer, setting, inlineCallbacks, SerialDeviceError, SerialConnectionError, PortRegError
from labrad.types import Error
from twisted.internet import reactor
from twisted.internet.defer import returnValue
from labrad.server import Signal
from labrad import types as T
from twisted.internet.task import LoopingCall
import time as time

SERVERNAME = 'ArduinoCounter'
TIMEOUT = 1.0
BAUDRATE = 57600
UPDATEREADINGID = 142879

class ArduinoCounter( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'ArduinoCounter'
    port = None
    serNode = 'qsimexpcontrol'
    timeout = T.Value(TIMEOUT,'s')
    on = False
    
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
            reactorlooptime = 0.1
            #not sure if loop can even run this fast, but must be faster than arduino 100ms PMT average , seems to work though
            yield reactor.callLater(reactorlooptime, self.getCounts)  
            reading = yield self.ser.readline()
            yield self.ser.flushinput()
            #reads arduino serial line output
            if reading:        
            #plots reading to data vault
                try:
                    yield self.dv.add(time.time() - self.start, float(reading)/100)
                    self.updatereading(float(reading)/100)
                except:
                    yield None
            else: yield None
        else: yield None
    @inlineCallbacks   
    def StopServer(self):
        yield self.ser.flushinput()
        
        
    @setting(1, "toggle counting", value = 'b')
    def toggleCounting(self,c,value):

        if value == True: 
            self.on = True
            self.getCounts()
        else:
            self.on = False
            
    @setting(2, "New Data Set", returns = 's')
    def newDataSet(self, c):
        filename = yield self.dv.new('PMT COUNTS',[('t', 'num')], [('kilocounts/sec','','num')])
        window_name = 'q'
        yield self.dv.add_parameter('Window', window_name)
        yield self.dv.add_parameter('plotLive', True)
        self.start = time.time()
#        self.getCounts()
        returnValue( filename[1] )
        
    
    
if __name__ == "__main__":
    from labrad import util
    util.runServer( ArduinoCounter() )
