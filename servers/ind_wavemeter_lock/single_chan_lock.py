"""
### BEGIN NODE INFO
[info]
name = Single WM Lock Server
version = 1.0
description =
instancename = Single WM Lock Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from twisted.internet.defer import returnValue
import os
import time
from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
import os
import socket


class ind_WM_lock_Server(LabradServer):

    name = 'Single WM Lock Server'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Single WM Lock Server'
        self.set = 811.291420
        self.volt = 0.0
        self.timer = 0.1
        self.rails = [-2.0, 2.0]
        self.gain = 1500.0
        self.prevoutput = 0.0
        self.dac = 3
        self.chan = 1
        self.lc = LoopingCall(self.loop)
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions

        """

        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync('10.97.112.2',
                                      name=self.name,
                                      password=self.password)
        self.server = self.cxn.multiplexerserver
        self.switchmode = yield self.server.get_switcher_mode()

    @inlineCallbacks
    def loop(self):
            freq = yield self.server.get_frequency(self.chan)
            error = -1*(self.set - freq)
            output = error*self.gain + self.prevoutput
            if output >= self.rails[1]:
                output = self.rails[1]
            elif output <= self.rails[0]:
                output = self.rails[0]
            else:
                pass
            self.prevoutput = output
            self.server.set_dac_voltage(self.dac, output)

    @setting(13, state='b')
    def toggle(self, c, state):
        '''
        Sends switches cal vs switcher
        '''
        if state:
            self.lc.start(self.timer)
        else:
            self.lc.stop()

    @setting(14, value='v')
    def offset(self, c, value):
        yield self.server.set_dac_voltage(3, value)
        self.prevoutput = value

    @setting(15, gain='v')
    def set_gain(self, c, gain):
        self.gain = gain

    @setting(16, setpoint='v')
    def set_point(self, c, setpoint):
        self.set = setpoint


if __name__ == "__main__":
    from labrad import util
    util.runServer(ind_WM_lock_Server())
