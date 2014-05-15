from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import returnValue
from twisted.internet.threads import deferToThread
from ctypes import c_long, c_double, c_buffer, c_float, c_int, windll, pointer
from Multiplexer_config import multiplexer_config
from labrad.units import WithUnit

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

SIGNALID1 = 122484

class MultiplexerServer(LabradServer):
    """
    Multiplexer Server for Wavelength Meter
    """
    name = 'Multiplexerserver'
    
    freqSignal = Signal(SIGNALID1, 'signal: new frequency measured', '(sv)')
    
    def initServer(self):
        
        self.d = c_double(0)
        self.l = c_long(0)        
        self.wmdll = windll.LoadLibrary("C:\Windows\System32\wlmData.dll")
        self.wmdll.SetDeviationSignalNum.restype = c_double
        self.wmdll.GetFrequencyNum.restype = c_double  
        self.wmdll.GetDeviationSignalNum.restype = c_double
        self.wmdll.GetActiveChannel.restype = c_long
        self.wmdll.GetExposureNum.restype = c_long
        self.wmdll.SetExposureNum.restype = c_long
        self.listeners = set()
        
    @setting(1, "Check WLM Running")
    def instance(self,c):
        instance = self.wmdll.Instantiate
        instance.restype = c_long
        RFC = c_long(-1)
        status = yield instance(RFC,self.l,self.l,self.l)
        returnValue(status)

        
    @setting(11, "Set Output Voltage", mV = ['v'])
    def setOutputVoltage(self,c,mV):
        yield self.wmdll.SetDeviationSignalNum(self.chanNum, mV)
        
    @setting(12, "Set Exposure Time", chan = 'i', ms = 'i')
    def setExposureTime(self,c,chan,ms):
        ms = c_long(ms)
        chan = c_long(chan)
        yield self.wmdll.SetExposureNum(chan,1,  ms)


    @setting(20,"Get Frequency", chan = 'i', returns = 'v')
    def getFrequency(self, c, chan):
        chan = c_long(chan)
        freq = yield self.wmdll.GetFrequencyNum(chan,self.d)
        self.freqSignal = freq
        returnValue(freq)
        
    @setting(21,"Get Output Voltage", chan = 'i', returns = 'v')
    def getOutputVoltage(self, c, chan):
        chan = c_long(chan)
        volts = yield self.wmdll.GetDeviationSignalNum(chan,self.d)
        returnValue(volts)  
        
    @setting(23, "Get Exposure", chan = 'i', returns = 'i')
    def getExp(self, c, chan): 
        chan = c_long(chan)
        exp = yield self.wmdll.GetExposureNum(chan ,1,self.l) 
        returnValue(exp)
        
        
if __name__ == "__main__":
    from labrad import util
    util.runServer(MultiplexerServer())
    
    