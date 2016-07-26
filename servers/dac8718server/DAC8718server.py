"""
### BEGIN NODE INFO
[info]
name = DAC8718 Server
version = 1.0
description =
instancename = DAC8718 Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""


'''
Created on July 16, 2015

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


SERVERNAME = 'DAC8718 Server'
TIMEOUT = 1.0
BAUDRATE = 9600


class ArduinoDAC(SerialDeviceServer):
    name = SERVERNAME
    regKey = 'DAC8718'
    port = None
    serNode = getNodeName()
    timeout = T.Value(TIMEOUT, 's')

    @inlineCallbacks
    def initServer(self):
        if not self.regKey or not self.serNode:
            error_message = 'Must define regKey and serNode attributes'
            raise SerialDeviceError(error_message)
        port = yield self.getPortFromReg(self.regKey)
        self.port = port
        try:
            serStr = yield self.findSerial(self.serNode)
            self.initSerial(serStr, port, baudrate=BAUDRATE)
        except SerialConnectionError, e:
            self.ser = None
            if e.code == 0:
                print 'Could not find serial server for node: %s' % self.serNode
                print 'Please start correct serial server'
            elif e.code == 1:
                print 'Error opening serial connection'
                print 'Check set up and restart serial server'
            else:
                raise

    @setting(1, chan='i', value='i')
    def DACOutput(self, c, chan, value):
        """
        Output voltage value (in bits from 0 to 2^16) on chan.

        Parameters
        ----------
        chan: int, DAC channel, valid from 0-15
        """
        chan = chan + 8
        if value > 2**16 - 1:
            value = 2**16 - 1
        elif value < 0:
            value = 0

        value = bin(value)[2:]

        if len(value) != 16:
            buff = 16 - len(value)
            value = '0'*buff + value

        value1 = value[0:8]
        value1 = int('0b' + value1, 2)
        value2 = value[8:]
        value2 = int('0b' + value2, 2)
        yield self.ser.write(chr(chan))
        yield self.ser.write(chr(value1))
        yield self.ser.write(chr(value2))

if __name__ == "__main__":
    from labrad import util
    util.runServer(ArduinoDAC())
