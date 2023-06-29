"""
### BEGIN NODE INFO
[info]
name = AWG Server
version = 1.0
description =
instancename = AWGServer

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

import pyvisa
from labrad.server import LabradServer
from labrad.server import setting
from twisted.internet.defer import inlineCallbacks


class AWG_Server(LabradServer):
    """
    Basic Server
    """

    name = 'AWG Server'

    def initServer(self):
        # self.password = os.environ['LABRADPASSWORD']
        print("I'm here")
        self.name = 'AWG Server'
        self.connect_to_AWG()

    @inlineCallbacks
    def connect_to_AWG(self):
        """
        """
        rm = pyvisa.ResourceManager()
        self.inst = yield rm.open_resource('TCPIP::10.97.112.68::INSTR')
        try:
            self.inst.query("*IDN?")
        except:
            pass
        #test
        print(self.inst.query("*IDN?"))

    @setting(1, returns='s')
    def test(self):
        print(self.inst.query("*IDN?"))


if __name__ == "__main__":
    from labrad import util
    util.runServer(AWG_Server())
