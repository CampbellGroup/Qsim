"""
### BEGIN NODE INFO
[info]
name = Multipole Monitor
version = 1.0
description =
instancename = Multipole Monitor

[startup]
cmdline = %PYTHON% %FILE%
timeout = 1000

[shutdown]
message = 987654321
timeout = 1000
### END NODE INFO
"""
from twisted.internet.defer import returnValue
import os
import time
from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
import socket


class multipole_monitor(LabradServer):
    """
    Server to monitor multipole voltages
    """
    name = 'Multipole Monitor'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = 'Multipole Monitor'
        self.rate = 60  # seconds between multipole readings
        self.time = 0
        connected = self.connect()


    @inlineCallbacks
    def connect(self):
        """
        Creates asynchronous connection
        """
        from labrad.wrappers import connectAsync

        # connect to multipole server and datavault computers

        self.cxn = yield connectAsync('10.97.112.4',
                                       name=self.name,
                                       password=self.password)
        # connect to servers
        self.server = yield self.cxn.multipole_server()

        # start looping call after connections are made to the desired servers
        self.lc = LoopingCall(self.loops)
        self.lc.start(self.rate)

        try:
            self.dv = yield self.cxn.servers['Data Vault']
        except KeyError as error:
            error_msg = str(error) + '  ' + 'DataVault is not running'
            raise KeyError(error_msg)

        self.path = yield self.setup_datavault('Time', 'Multipole Values [V]')

    @inlineCallbacks
    def loops(self):

        # grab the multipoles
        mps = yield self.server.get_multipoles()
        self.time = self.time + self.rate

        # yield self.dv.add(self.time, mps[0], mps[1], mps[2], mps[3], mps[4], mps[5], mps[6], mps[7])


    @inlineCallbacks
    def setup_datavault(self, x_axis, y_axis):
        """
        adds parameters to datavault and parameter vault, define contexts for each laser
        """
        yield self.dv.cd(['', self.name], True)
        self.dataset = yield self.dv.new(self.name, [( 't', 'num')], [('Ex', '', 'num')], [('Ey', '', 'num')], [('Ez', '', 'num')], [('M1', '', 'num')], [('M2', '', 'num')], [('M3', '', 'num')], [('M4', '', 'num')], [('M5', '', 'num')])


if __name__ == "__main__":
    from labrad import util
    util.runServer(multipole_monitor())
