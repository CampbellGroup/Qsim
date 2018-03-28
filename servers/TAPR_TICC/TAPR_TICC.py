"""
### BEGIN NODE INFO
[info]
name = ArduinoTDC
version = 1.0
description =
instancename = ArduinoTDC

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.types import Value
from labrad.devices import DeviceServer, DeviceWrapper
from labrad.server import setting
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.task import LoopingCall

TIMEOUT = Value(1.0, 's')


class TDCDevice(DeviceWrapper):

    @inlineCallbacks
    def connect(self, server, port):
        """Connect to a TDC device."""
        print 'connecting to "%s" on port "%s"...' % (server.name, port),
        self.server = server
        self.ctx = server.context()
        self.port = port
        self.most_recent = 0.0
        p = self.packet()
        p.open(port)
        p.baudrate(115200)
        p.read()  # clear out the read bfrom twisted.internet.task import LoopingCalluffer
        p.timeout(TIMEOUT)
        yield p.send()
        self.timeInterval = 0.1
        self.loop = LoopingCall(self.main_loop)
        self.loopDone = self.loop.start(self.timeInterval, now=True)

    def packet(self):
        """Create a packet in our private context."""
        return self.server.packet(context=self.ctx)

    def shutdown(self):
        """Disconnect from the serial port when we shut down."""
        return self.packet().close().send()

    @inlineCallbacks
    def write(self, code):
        """Write a data value to the heat switch."""
        yield self.packet().write_line(code).send()

    @inlineCallbacks
    def query(self, code):
        """ Write, then read. """
        p = self.packet()
        p.write_line(code)
        p.read_line()
        ans = yield p.send()
        returnValue(ans.read_line)

    @inlineCallbacks
    def read_line(self):
        """ Read. """
        p = self.packet()
        p.read_line()
        ans = yield p.send()
        returnValue(ans.read_line)

    @inlineCallbacks
    def read_all(self):
        """ Read. """
        p = self.packet()
        p.read()
        ans = yield p.send()
        returnValue(ans.read)

    @inlineCallbacks
    def main_loop(self):

        value = yield self.read_line()
        try:
            value = float(value[0:14])
            self.most_recent = value
        except:
            pass


class ArduinoTDC(DeviceServer):
    name = 'ArduinoTDC'
    deviceName = 'ArduinoTDC'
    deviceWrapper = TDCDevice

    @inlineCallbacks
    def initServer(self):
        self.reg = self.client.registry()
        yield self.loadConfigInfo()
        yield DeviceServer.initServer(self)

    @inlineCallbacks
    def loadConfigInfo(self):
        """Load configuration information from the registry."""
        reg = self.reg
        yield reg.cd(['', 'Servers', 'ArduinoTDC', 'Links'], True)
        dirs, keys = yield reg.dir()
        print dirs
        p = reg.packet()
        for k in keys:
            p.get(k, key=k)
        ans = yield p.send()
        self.serialLinks = dict((k, ans[k]) for k in keys)

    @inlineCallbacks
    def findDevices(self):
        """Find available devices from list stored in the registry."""
        devs = []
        for name, (serServer, port) in self.serialLinks.items():
            if serServer not in self.client.servers:
                continue
            server = self.client[serServer]
            ports = yield server.list_serial_ports()
            print port
            if port not in ports:
                continue
            devName = '%s - %s' % (serServer, port)
            devs += [(devName, (server, port))]
        returnValue(devs)

    @setting(199)
    def clear_data(self, c):
        dev = self.selectDevice(c)
        data = yield dev.read_all()
        returnValue(data)


    @setting(200, returns='v')
    def get_most_recent_data(self, c):
        dev = self.selectDevice(c)
        value = yield dev.most_recent
        returnValue(value)

if __name__ == "__main__":
    from labrad import util
    util.runServer(ArduinoTDC())
