"""
### BEGIN NODE INFO
[info]
name = Cavity Piezo Lock
version = 1.0
description =
instancename = Cavity Piezo Lock Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from labrad.units import WithUnit as U
import os
import socket

class cavity_piezo_lock(LabradServer):

    name = 'Cavity Piezo Lock Server'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Cavity Piezo Lock Server'
        self.set = 812.124890
        self.freq_span = 0.0001
        self.volt = 0.0
        self.timer = 1.0
        self.rails = [0, .4]
        self.gain = -0.1
        self.prevoutput = 0.0
        self.chan = 1
        self.lc = LoopingCall(self.loop)
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions

        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name='Cavity Piezo Lock Server')
        self.server = self.cxn.multiplexerserver
        self.pzt = self.cxn.piezo_server

        # need to select the device and correct pzt channel here still
