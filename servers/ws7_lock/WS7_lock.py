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

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from labrad.units import WithUnit as U
import os
import socket


class ind_WM_lock_Server(LabradServer):

    name = 'WS7 Lock Server'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Single WM Lock Server'
        self.set = 752.451900
        self.freq_span = 0.001
        self.volt = 0.0
        self.timer = 1.0
        self.rails = [0, .4]
        self.gain = -0.1
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
        self.cxn = yield connectAsync(name='WS7 lock Server')
        self.server = self.cxn.multiplexerserver
        self.dac = self.cxn.keithley_2230g_server
        yield self.dac.select_device(0)
        yield self.dac.output(2, True)

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

            if (freq >= (freq - self.freq_span)) or (freq <=(freq + self.freq_span)):
                output = self.prevoutput
            self.prevoutput = output
            yield self.dac.voltage(2, U(output, 'V'))
            #self.server.set_dac_voltage(self.dac, output)

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
        #yield self.server.set_dac_voltage(self.dac, value)
        print value
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
