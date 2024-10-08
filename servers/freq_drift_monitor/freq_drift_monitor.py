"""
### BEGIN NODE INFO
[info]
name = Frequency Monitor
version = 1.0
description =
instancename = Frequency Monitor

[startup]
cmdline = %PYTHON% %FILE%
timeout = 100

[shutdown]
message = 987654321
timeout = 100
### END

"""

import os
import time
from labrad.server import LabradServer
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
import socket


class freq_drift_monitor(LabradServer):
    """
    Server to monitor frequencies for multiple lasers, and display drift over time
    """

    name = "Frequency Monitor"

    def initServer(self):
        self.password = os.environ["LABRADPASSWORD"]
        self.name = socket.gethostname() + " Frequency Monitor"
        self.chan = [8]  # wavemeter channels to monitor
        self.set_freq = [0.0]  # desired frequencies
        self.rate = 6  # seconds between wavemeter readings
        self.time = 0
        self.connect()
        self.lc = LoopingCall(self.loop)
        self.lc.start(self.rate)

    @inlineCallbacks
    def connect(self):
        """
        Creates asynchronous connection
        """
        from labrad.wrappers import connectAsync

        self.cxn = yield connectAsync(
            "10.97.112.2", name=self.name, password=self.password
        )
        print("before")
        self.server = self.cxn.multiplexerserver

        try:
            self.dv = self.cxn.servers["Data Vault"]
        except KeyError as error:
            error_msg = str(error) + "\n" + "DataVault is not running"
            raise KeyError(error_msg)

        try:
            self.grapher = self.cxn.servers["grapher"]
        except:
            self.grapher = None

        self.path = yield self.setup_datavault("Time", "Frequency Monitor")
        yield self.setup_grapher("Frequency Monitor")

    @inlineCallbacks
    def loop(self):
        freq0 = yield self.server.get_frequency(self.chan[0])
        print("after")
        drift0 = self.set_freq[0] - freq0
        self.time = self.time + self.rate

        yield self.dv.add(time, drift0)

    # freq = [yield self.server.get_frequency(self.chan[i]) for i in range(len(self.chan))]

    @inlineCallbacks
    def setup_datavault(self, x_axis, y_axis):
        """
        adds parameters to datavault and parameter vault
        """

        self.dv.cd(["", self.name], True)
        self.dataset = yield self.dv.new(
            self.name, [(x_axis, "num")], [(y_axis, "", "num")]
        )

    @inlineCallbacks
    def setup_grapher(self, tab):
        yield self.grapher.plot(self.dataset, tab, False)


if __name__ == "__main__":
    from labrad import util

    util.runServer(freq_drift_monitor())
