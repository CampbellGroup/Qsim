"""
### BEGIN NODE INFO
[info]
name = drift_tracker
version = 1.0
description =
instancename = drift_tracker
[startup]
cmdline = %PYTHON% %FILE%
timeout = 20
[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer
from twisted.internet.defer import inlineCallbacks
from twisted.internet.task import LoopingCall
from drift_config import drift_tracker_config as hc


class driftTracker(LabradServer):

    name = 'drift_tracker'

    def initServer(self):
        self.tracked_servers = {}
        self.tracked_items = hc.info
        self.connect()

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        self.cxn = yield connectAsync(name='Drift Tracker')
        yield self.setupListeners()
        self.tracked_servers = []
        for key, value in self.tracked_items.iteritems():
            self.tracked_servers = value[0]
            print self.tracked_servers

        self.fast_loop = LoopingCall(self.update_fast_loop)
        self.slow_loop = LoopingCall(self.update_slow_loop)
        self.fast_loop.start(10)

    @inlineCallbacks
    def setupListeners(self):
        yield self.client.manager.subscribe_to_named_message('Server Connect', 9291932, True)
        yield self.client.manager.subscribe_to_named_message('Server Disconnect', 9292932, True)
        yield self.client.manager.addListener(listener=self.followServerConnect,
                                              source=None,
                                              ID=9291932)
        yield self.client.manager.addListener(listener=self.followServerDisconnect,
                                              source=None,
                                              ID=9292932)

    @inlineCallbacks
    def followServerDisconnect(self, ctx, serverName):
        serverName = serverName[1]
        print serverName
        if serverName in self.tracked_servers:
            print 'tracked server!'
            yield None

    @inlineCallbacks
    def followServerConnect(self, ctx, serverName):
        serverName = serverName[1]
        print serverName
        if serverName in self.tracked_servers:
            print 'tracked server online!'
            yield None

    @inlineCallbacks
    def update_slow_loop(self):
        pass

    @inlineCallbacks
    def update_fast_loop(self):

        for key, value in self.tracked_items.iteritems():
            server_name = value[0]
            server_name = server_name.replace(' ', '_').lower()
            method_name = value[1]
            arg = value[2]
            server = getattr(self.cxn, server_name)
            method = getattr(server, method_name)
            if arg is None:
                ans = yield method()
            else:
                ans = yield method(arg)
            self.update_grapher(key, ans)

    @inlineCallbacks
    def update_grapher(self, plot, data):
        print plot, data
        yield None


if __name__ == "__main__":
    from labrad import util
    util.runServer((driftTracker()))
