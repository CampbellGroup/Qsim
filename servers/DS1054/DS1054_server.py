"""
### BEGIN NODE INFO
[info]
name = DS1054 Scope Server
version = 1.0
description =
instancename = DS1054 Scope Server

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

dev_name = '/dev/usbtmc0'


class DS1054_Server(LabradServer):

    name = 'DS1054 Scope Server'

    def initServer(self):
        self.device = os.open(dev_name, os.O_RDWR)

    @setting(11, returns='s')
    def query_device(self, c):
        self.write("*IDN?")
        response = self.read(data_size=40)
        yield returnValue(response)

    @setting(13, chan='w', returns='s')
    def measureVPP(self, c, chan):
        self.write(':MEAS:ITEM VAVG,CHAN' + str(chan))
        self.write(':MEAS:ITEM? VAVG,CHAN' + str(chan))
        #time.sleep(0.1)
        #self.write(':MEAS:VPP? [CHAN' + str(chan) + ']')
        response = self.read(data_size=300)
        yield returnValue(response)

    def write(self, data):
        os.write(self.device, data)

    def read(self, data_size=40):
        data = os.read(self.device, data_size)
        return data


if __name__ == "__main__":
    from labrad import util
    util.runServer(DS1054_Server())
