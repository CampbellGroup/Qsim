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
from labrad.server import Signal
from labrad import types as T
from twisted.internet.task import LoopingCall
import time as time

SERVERNAME = 'ArduinoCounter'
TIMEOUT = 1.0
BAUDRATE = 57600

class ArduinoCounter( SerialDeviceServer ):
    name = SERVERNAME
    regKey = 'ArduinoCounter'
    port = None
    serNode = 'tony-dell'
    timeout = T.Value(TIMEOUT,'s')
    
    
    @inlineCallbacks
    def initServer( self ):
        if not self.regKey or not self.serNode: raise SerialDeviceError( 'Must define regKey and serNode attributes' )
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
        self.saveFolder = ['','PMT Counts test']
        self.dataSetName = 'PMT Counts test '
        yield self.connect_data_vault()
        self.filename = yield self.dv.new('PMT COUNTS test',[('t', 'num')], [('kilocounts/sec','','num')])
        self.start = time.time()
#        self.timeInterval = 1 # how often to call the loop function in seconds
#        self.loop = LoopingCall(self.getCounts())
        self.getCounts()
#        self.loopDone = self.loop.start(self.timeInterval, now=True)
                    
    @inlineCallbacks
    def connect_data_vault(self):
        try:
            #reconnect to data vault and navigate to the directory
            self.dv = yield self.client.data_vault
            yield self.dv.cd(self.saveFolder, True)    
            print 'Connected: Data Vault'
        except AttributeError:
            self.dv = None
            print 'Not Connected: Data Vault'
            
    @inlineCallbacks
    def stopServer(self):
        self.loop.stop()
        yield self.loopDone
        
            
    @inlineCallbacks
    def getCounts(self):
        reactor.callLater(.05, self.getCounts)
        reading = yield self.ser.readline()
        if reading:        
            self.dv.add(time.time() - self.start, float(reading)/100)
    
if __name__ == "__main__":
    from labrad import util
    util.runServer( ArduinoCounter() )
