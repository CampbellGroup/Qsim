"""
### BEGIN NODE INFO
[info]
name = Laser Monitor
version = 1.0
description =
instancename = Laser Monitor

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


class laser_drift_monitor(LabradServer):
    """
    Server to monitor frequencies for multiple lasers, and display drift over time
    """
    name = 'Laser Monitor'

    def initServer(self):
        self.password = os.environ['LABRADPASSWORD']
        self.name = 'Laser Monitor'
        self.chan = [ 4, 8, 0]  # wavemeter channels to monitor [ 935, 638, 369/399]
        self.set_freq171 = [ 320.568940, 469.445150, 812.109250, 752.452635]  # desired frequencies of lasers for Yb171
        self.set_freq174 = [ 320.571657, 469.439000, 812.111480, 752.451800 ]   # desired frequencies of lasers for Yb174
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
        self.cxn = yield connectAsync('10.97.112.2',
                                      name=self.name,
                                      password=self.password)
        self.cxn1 = yield connectAsync('10.97.112.4',
                                       name=self.name,
                                       password=self.password)
        # connect to servers
        self.server = yield self.cxn.multiplexerserver
        self.server1 = yield self.cxn1.multiplexerserver

        #determine if trying to load 171 or 174 based on 935 frequency
        freq935 = yield self.server.get_frequency(self.chan[0])
        if freq935 > 320.570:
            self.set_freq = self.set_freq174
        else:
            self.set_freq = self.set_freq171

        # start looping call after connections are made to the desired servers
        self.lc = LoopingCall(self.loops)
        self.lc.start(self.rate)

        try:
            self.dv = yield self.cxn1.servers['Data Vault']
        except KeyError as error:
            error_msg = str(error) + '  ' + 'DataVault is not running'
            raise KeyError(error_msg)

        try:
            self.grapher = self.cxn1.servers['grapher']
        except:
            self.grapher = None

        self.path = yield self.setup_datavault('Time', 'Laser Monitor')

        # setup the graphers for each drift monitor plot
        yield self.setup_grapher935('935')
        yield self.setup_grapher638('638')
        yield self.setup_grapher369('369')
        yield self.setup_grapher399('399')

    @inlineCallbacks
    def loops(self):

        # grab the freqs
        freq0 = yield self.server.get_frequency(self.chan[0])
        freq1 = yield self.server.get_frequency(self.chan[1])
        freq2 = yield self.server1.get_frequency(self.chan[2])

        # calc detunings from desired 171 freqs in MHz, wavemeter gives THz
        drift0, drift1, drift2 = 1000000*(self.set_freq[0] - freq0), 1000000*(self.set_freq[1] - freq1), 1000000*(self.set_freq[2] - freq2)

        # update the clock
        self.time = self.time + self.rate

        # add 935 and 638 from wavemeter switch to datavault
        yield self.dv.add(self.time, drift0, context = self.ctx935)
        yield self.dv.add(self.time, drift1, context = self.ctx638)

        # determine if wavemeter is seeing 369 pr 399 based on 369 set freq, then add data to appropriate plot, 10 GHz discriminator
        if drift2 < 10000:
            yield self.dv.add(self.time, drift2, context = self.ctx369)
        else:
            drift2 = 1000000*(self.set_freq[3] - freq2)
            yield self.dv.add(self.time, drift2, context = self.ctx399)

    @inlineCallbacks
    def setup_datavault(self, x_axis, y_axis):
        """
        adds parameters to datavault and parameter vault, define contexts for each laser
        """
        self.ctx638 = self.dv.context()
        self.ctx935 = self.dv.context()
        self.ctx369 = self.dv.context()
        self.ctx399 = self.dv.context()

        yield self.dv.cd(['', self.name], True)

        # datasets for each laser
        self.dataset935 = yield self.dv.new(self.name + ' 935', [( 't', 'num')], [('MHz', '', 'num')], context = self.ctx935)
        self.dataset638 = yield self.dv.new(self.name + ' 638', [( 't', 'num')], [('MHz', '', 'num')], context = self.ctx638)
        self.dataset369 = yield self.dv.new(self.name + ' 369', [( 't', 'num')], [('MHz', '', 'num')], context = self.ctx369)
        self.dataset399 = yield self.dv.new(self.name + ' 399', [( 't', 'num')], [('MHz', '', 'num')], context = self.ctx399)

    @inlineCallbacks
    def setup_grapher935(self, tab):
        yield self.grapher.plot(self.dataset935, tab, False)

    @inlineCallbacks
    def setup_grapher638(self, tab):
        yield self.grapher.plot(self.dataset638, tab, False)

    @inlineCallbacks
    def setup_grapher369(self, tab):
        yield self.grapher.plot(self.dataset369, tab, False)

    @inlineCallbacks
    def setup_grapher399(self, tab):
        yield self.grapher.plot(self.dataset399, tab, False)

if __name__ == "__main__":
    from labrad import util
    util.runServer(laser_drift_monitor())
