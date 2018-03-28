"""
### BEGIN NODE INFO
[info]
name = Multipole Server
version = 1.0
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

from twisted.internet.defer import returnValue
from labrad.server import LabradServer, setting
from twisted.internet.defer import inlineCallbacks
from config.dac_ad660_config import hardwareConfiguration as hc
from twisted.internet.task import LoopingCall
import socket
import numpy as np


class Electrode():

    def __init__(self, dac, octant, minval, maxval):

        self.dac = dac
        self.octant = octant
        self.minval = minval
        self.maxval = maxval
        self.name = str('DAC: ' + str(dac))


class Multipole_Server(LabradServer):

    name = 'Multipole Server'

    def initServer(self):
        self.name = socket.gethostname() + ' Multipole Server'

        self.hc = hc
        self.M = self.hc.M
        self.lc = LoopingCall(self.loop)
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to dac8718 Server and
        connects incoming signals to relavent functions

        """

        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name='Multipole Server')
        try:
            self.server = self.cxn.dac_ad660_server
        except:
            self.server = None
        self.reg = self.cxn.registry

        yield self.reg.cd(['', 'settings'], True)
        self.multipoles = yield self.reg.get('Multipoles')

        self.electrodes = {}
        for chan_name, channel in self.hc.elec_dict.iteritems():
            electrode = Electrode(channel.dacChannelNumber, channel.octantNumber,
                                  minval = -10.0, maxval = 10.0)
            self.electrodes[electrode.octant] = electrode
            #self.update_dac(0.0, channel)

        self.lc.start(5.0)  # start registry saving looping call

    @inlineCallbacks
    def setupListeners(self):
        yield self.client.manager.subscribe_to_named_message('Server Connect', 9898689, True)
        yield self.client.manager.subscribe_to_named_message('Server Disconnect', 9398989, True)

    @inlineCallbacks
    def followServerConnect(self, cntx, serverName):
        serverName = serverName[1]
        if serverName == 'dac8718':
            yield self.client.refresh()
            yield self.connect()

    @inlineCallbacks
    def followServerDisconnect(self, cntx, serverName):
        serverName = serverName[1]
        if serverName == 'dac8718':
            self.server = None

    @setting(16, Mvector='*v', returns='*v')
    def set_multipoles(self, c, Mvector):
        Mvector = np.array(Mvector)
        Evector = self.M.dot(Mvector)
        if max(Evector) >= 10.0:
            returnValue([])
        if min(Evector) <= -10.0:
            returnValue([])

        for octant, voltage in enumerate(Evector):
            yield self.update_dac(voltage, self.electrodes[octant + 1])
        self.multipoles = Mvector
        returnValue(Evector)

    @setting(17)
    def save_multipoles_to_registry(self, c):
        yield self.reg.set('Multipoles', self.multipoles)

    @setting(18, returns='*v')
    def get_multipoles(self, c):
        yield None
        returnValue(self.multipoles)

    @inlineCallbacks
    def update_dac(self, voltage, electrode):
        if len(str(electrode.dac)) == 1:
            dac = '0' + str(electrode.dac)
        else:
            dac = str(electrode.dac)
        if not self.server:
            returnValue('Server not Connected')
        yield self.server.set_individual_analog_voltages([(dac, voltage)])

    @inlineCallbacks
    def loop(self):
        yield self.reg.set('Multipoles', self.multipoles)


if __name__ == "__main__":
    from labrad import util
    util.runServer(Multipole_Server())
