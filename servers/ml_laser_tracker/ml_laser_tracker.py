"""
### BEGIN NODE INFO
[info]
name = ML Monitor
version = 1.0
description =
instancename = ML Monitor

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


class ml_laser_monitor(LabradServer):
    """
    Server to monitor frequencies for ML lasers, and display drift over time
    """

    name = "ML Monitor"

    def initServer(self):
        self.password = os.environ["LABRADPASSWORD"]
        self.name = "ML Monitor"
        self.chan = [0]  # wavemeter channels to monitor [ 935, 638, 369/399]
        self.set_freq = [405645.000]  # desired frequencies of lasers
        self.rate = 2  # seconds between wavemeter readings
        self.time = 0
        connected = self.connect()

    @inlineCallbacks
    def connect(self):
        """
        Creates asynchronous connection
        """
        from labrad.wrappers import connectAsync

        # connect to wavemeter and datavault computers
        self.cxn = yield connectAsync(
            "10.97.112.1", name=self.name, password=self.password
        )
        self.cxn1 = yield connectAsync(
            "10.97.112.4", name=self.name, password=self.password
        )
        # connect to servers
        self.server = yield self.cxn1.bristol_521

        # start looping call after connections are made to the desired servers
        self.lc = LoopingCall(self.loops)
        self.lc.start(self.rate)

        try:
            self.dv = yield self.cxn.servers["Data Vault"]
        except KeyError as error:
            error_msg = str(error) + "  " + "DataVault is not running"
            raise KeyError(error_msg)

        try:
            self.grapher = self.cxn1.servers["grapher"]
        except:
            self.grapher = None

        self.path = yield self.setup_datavault("Time", "ML Monitor")

        # setup the graphers for each drift monitor plot
        yield self.setup_grapher("ML Monitor")

    @inlineCallbacks
    def loops(self):

        # grab the freqs
        freq0 = yield self.server.get_wavelength()

        # calc detunings from desired 171 freqs in MHz, wavemeter gives THz
        drift0 = self.set_freq[0] - freq0

        # update the clock
        self.time = self.time + self.rate

        # add 935 and 638 from wavemeter switch to datavault
        yield self.dv.add(self.time, drift0)

    @inlineCallbacks
    def setup_datavault(self, x_axis, y_axis):
        """
        adds parameters to datavault and parameter vault, define contexts for each laser
        """

        yield self.dv.cd(["", self.name], True)

        # datasets for each laser
        self.dataset = yield self.dv.new(
            self.name + " ML", [("t", "num")], [("GHz", "", "num")]
        )

    @inlineCallbacks
    def setup_grapher(self, tab):
        yield self.grapher.plot(self.dataset, tab, False)


if __name__ == "__main__":
    from labrad import util

    util.runServer(ml_laser_monitor())
