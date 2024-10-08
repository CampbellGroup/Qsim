"""
### BEGIN NODE INFO
[info]
name = Multipole Server
version = 1.1
description =
instancename = Multipole Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

import socket

import numpy as np
from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks
from twisted.internet.defer import returnValue
from twisted.internet.task import LoopingCall

from config.dac_ad660_config import HardwareConfiguration as HC
from config.dac_ad660_config import MultipoleConfiguration as MC


class MultipoleServer(LabradServer):
    name = "Multipole Server"

    def initServer(self):
        self.name = socket.gethostname() + " Multipole Server"

        self.M = MC.M
        self.lc = LoopingCall(self.loop)
        self.connect()

    @inlineCallbacks
    def connect(self):
        """
        Creates an Asynchronous connection to dac8718 Server and
        connects incoming signals to relevant functions
        """

        from labrad.wrappers import connectAsync

        self.cxn = yield connectAsync(name="Multipole Server")
        try:
            self.server = self.cxn.dac_ad660_server
        except:
            self.server = None
        self.reg = self.cxn.registry

        yield self.reg.cd(["", "settings"], True)
        self.multipoles = yield self.reg.get("Multipoles")

        self.dac_channels = []
        for i, channel in enumerate(HC.dac_channels):
            self.dac_channels.append(channel.dac_channel_number)
            # self.update_dac(0.0, channel)

        self.lc.start(5.0)  # start registry saving looping call

    @inlineCallbacks
    def setup_listeners(self):
        yield self.client.manager.subscribe_to_named_message(
            "Server Connect", 9898689, True
        )
        yield self.client.manager.subscribe_to_named_message(
            "Server Disconnect", 9398989, True
        )

    @inlineCallbacks
    def follow_server_connect(self, cntx, server_name):
        server_name = server_name[1]
        if server_name == "dac8718":
            yield self.client.refresh()
            yield self.connect()

    @inlineCallbacks
    def follow_server_disconnect(self, cntx, server_name):
        server_name = server_name[1]
        if server_name == "dac8718":
            self.server = None

    @setting(16, mvector="*v", returns="*v")
    def set_multipoles(self, c, mvector):
        mvector = np.array(mvector)
        evector = self.M.dot(mvector)

        for i, voltage in enumerate(evector):
            yield self.update_dac(voltage, self.dac_channels[i])
        self.multipoles = mvector
        returnValue(evector)

    @setting(17)
    def save_multipoles_to_registry(self, c):
        yield self.reg.set("Multipoles", self.multipoles)

    @setting(18, returns="*v")
    def get_multipoles(self, c):
        yield None
        returnValue(self.multipoles)

    @inlineCallbacks
    def update_dac(self, voltage, dac_num):
        if not self.server:
            returnValue("Server not Connected")
        yield self.server.set_individual_analog_voltages([(dac_num, voltage)])

    @inlineCallbacks
    def loop(self):
        yield self.reg.set("Multipoles", self.multipoles)


if __name__ == "__main__":
    from labrad import util

    util.runServer(MultipoleServer())
