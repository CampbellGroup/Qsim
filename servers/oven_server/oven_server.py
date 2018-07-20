"""
### BEGIN NODE INFO
[info]
name = Oven_Server
version = 1.0
description =
instancename = OvenServer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall
import os
import socket
from labrad.units import WithUnit as U


class OvenServer(LabradServer):

    name = 'OvenServer'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = socket.gethostname() + ' Oven Server'
        self.max_current = U(3.00, 'A')
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relavent functions

        """
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name='Oven_Server')
        self.server = self.cxn.keithley_2230g_server
        yield self.server.select_device(0)
        yield self.server.output(3, False)
        self.oven_state = False

    @setting(16, value='v[A]')
    def oven_current(self, c, value):
        if value <= self.max_current:
            yield self.server.current(3, value)
        else:
            returnValue('Current above max allowed')

    @setting(17, output='b')
    def oven_output(self, c, output):
        yield self.server.output(3, output)

    @setting(18, returns='b')
    def get_output(self, c):
        output = yield self.server.output(3)
        returnValue(output)

    @inlineCallbacks
    def stopServer(self):
        yield self.server.output(3, False)

if __name__ == "__main__":
    from labrad import util
    util.runServer(OvenServer())
