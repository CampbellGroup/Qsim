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
from config.dac_8718_config import dac_8718_config
import socket
import numpy as np


class Electrode():

    def __init__(self, dac, octant, minval, maxval, settings):

        self.dac = dac
        self.octant = octant
        self.minval = minval
        self.maxval = maxval
        self.name = str('DAC: ' + str(dac))


class Multipole_Server(LabradServer):

    name = 'Multipole Server'

    def initServer(self):
        self.name = socket.gethostname() + ' Multipole Server'

        self.config = dac_8718_config()
        self.minval = self.config.minval
        self.maxval = self.config.maxval
        self.M = self.config.M
        self.U = self.config.U
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to dac8718 Server and
        connects incoming signals to relavent functions

        """

        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name='Multipole Server')
        self.server = self.cxn.dac8718
        self.reg = self.cxn.registry

        yield self.reg.cd(['', 'settings'], True)
        self.multipoles = yield self.reg.get('Multipoles')

        self.electrodes = {}
        for channel in self.config.channels:
            electrode = Electrode(channel.dac, channel.octant,
                                  self.minval, self.maxval, self.settings)
            self.update_dac(0.0, channel)
            self.electrodes[electrode.octant] = electrode

    @setting(16, Mvector='*v', returns='*v')
    def set_multipoles(self, c, Mvector):
        Mvector = np.array(Mvector)
        Evector = self.M.dot(Mvector)
        if max(Evector) >= self.maxval:
            returnValue([])
        if min(Evector) <= self.minval:
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

    def volt_to_bit(self, volt):
        m = (2**16 - 1)/(self.maxval - self.minval)
        b = -1 * self.minval * m
        bit = int(m*volt + b)
        return bit

    @inlineCallbacks
    def update_dac(self, voltage, electrode):
        bit = self.volt_to_bit(voltage)
        yield self.server.dacoutput(electrode.dac, bit)


if __name__ == "__main__":
    from labrad import util
    util.runServer(Multipole_Server())
