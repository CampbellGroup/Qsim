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
import os
import socket
from labrad.units import WithUnit as U


class OvenServer(LabradServer):
    name = "OvenServer"

    def initServer(self):
        self.password = os.environ["LABRADPASSWORD"]
        self.name = socket.gethostname() + " Oven Server"
        self.max_current = U(5.00, "A")
        self.oven_channel = 3
        self.shutter_channel = 1
        self.protection_channel = 2
        self.connect()

    @inlineCallbacks
    def connect(self):
        """
        Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relevant functions
        """
        from labrad.wrappers import connectAsync

        self.cxn = yield connectAsync(name="Oven_Server")
        self.keithley = self.cxn.keithley_2230g_server

        yield self.keithley.select_device(0)
        yield self.keithley.output(self.oven_channel, False)
        yield self.keithley.output(self.shutter_channel, False)
        yield self.keithley.voltage(self.shutter_channel, U(5.0, "V"))
        yield self.keithley.current(self.shutter_channel, U(0.8, "A"))
        yield self.keithley.output(self.protection_channel, False)
        yield self.keithley.voltage(self.protection_channel, U(5.0, "V"))
        yield self.keithley.current(self.protection_channel, U(0.8, "A"))

    @setting(16, value="v[A]")
    def oven_current(self, c, value):
        if value <= self.max_current:
            yield self.keithley.current(self.oven_channel, value)
        else:
            returnValue(f"Current is above the max allowed ({str(self.max_current)})")

    @setting(17, output="b")
    def oven_output(self, c, output):
        yield self.keithley.output(self.oven_channel, output)

    @setting(19, output="b")
    def shutter_output_399(self, c, output):
        yield self.keithley.output(self.shutter_channel, output)

    @setting(20, output="b")
    def shutter_output_protection(self, c, output):
        yield self.keithley.output(self.protection_channel, output)

    @setting(18, returns="b")
    def get_output(self, c):
        output = yield self.keithley.output(self.oven_channel)
        returnValue(output)

    @inlineCallbacks
    def stopServer(self):
        yield self.keithley.output(3, False)


if __name__ == "__main__":
    from labrad import util

    util.runServer(OvenServer())
