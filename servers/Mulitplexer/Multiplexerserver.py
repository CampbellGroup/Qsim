from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import returnValue
from twisted.internet.threads import deferToThread
from ctypes import c_long, c_buffer, c_float, windll, pointer
from Multiplexer_config import multiplexer_config

"""
### BEGIN NODE INFO
[info]
name = Multiplexer Server
version = 1.0
description = 
instancename = Multiplexer Server

[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

class MultiplexerServer(LabradServer):
    """
    Multiplexer Server for Wavelength Meter
    """
    name = 'Multiplexerserver'
    def initServer(self):
        self.wmdll = windll.LoadLibrary("C:\Windows\System32\wlmData.dll")
        
    @setting(1,"Change Channel", chanNum = 'v')
    def changeChannel(self, c, chanNum):
        chanNum = int(chanNum)
        print chanNum
        yield self.wmdll.SetActiveChannel(1,1,chanNum,0)

        

if __name__ == "__main__":
    from labrad import util
    util.runServer(MultiplexerServer())
    
    