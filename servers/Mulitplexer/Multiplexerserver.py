from labrad.server import LabradServer, setting, Signal
from twisted.internet.defer import returnValue
from twisted.internet.threads import deferToThread
from ctypes import c_long, c_double, c_buffer, c_float, c_int, c_bool, windll, pointer
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
SIGNALID2 = 122485

class MultiplexerServer(LabradServer):
    """
    Multiplexer Server for Wavelength Meter
    """
    name = 'Multiplexerserver'
    
    expchanged  = Signal(SIGNALID1, 'signal: exposure changed', '(2i)')
    freqchanged = Signal(SIGNALID2, 'signal: frequency changed', '(iv)')
    #Set up signals to be sent to listeners
    
    def initServer(self):
        
        self.d = c_double(0)
        self.l = c_long(0)    
        self.b = c_bool(0)    
        self.wmdll = windll.LoadLibrary("C:\Windows\System32\wlmData.dll")
        #load wavemeter dll file for use of API functions self.d and self.l are dummy c_types for unused wavemeter functions
 
        self.wmdll.GetActiveChannel.restype        = c_long 
        self.wmdll.GetAmplitudeNum.restype         = c_long 
        self.wmdll.GetDeviationMode.restype        = c_bool      
        self.wmdll.GetDeviationSignalNum.restype   = c_double
        self.wmdll.GetExposureNum.restype          = c_long
        self.wmdll.GetFrequencyNum.restype         = c_double  
        self.wmdll.GetPIDCourseNum.restype         = c_long
        self.wmdll.GetSwitcherMode.restype         = c_long
        self.wmdll.GetSwitcherSignalStates.restype = c_long

        self.wmdll.SetDeviationMode.restype        = c_long
        self.wmdll.SetDeviationSignalNum.restype   = c_double
        self.wmdll.SetExposureNum.restype          = c_long 
        self.wmdll.SetPIDCourseNum.restype         = c_long              
        self.wmdll.SetSwitcherSignalStates.restype = c_long        
        self.wmdll.SetSwitcherMode.restype         = c_long
        
        #allocates c_types for dll functions
        
        self.listeners = set()

    @setting(1, "Check WLM Running")
    def instance(self,c):
        instance = self.wmdll.Instantiate
        instance.restype = c_long
        RFC = c_long(-1)    
        #RFC, reason for call, used to check if wavemeter is running (in wavemeter .h library
        status = yield instance(RFC,self.l,self.l,self.l)
        returnValue(status)

        
        
#####Main program functions        

         
    @setting(12, "Set Exposure Time", chan = 'i', ms = 'i')
    def setExposureTime(self,c,chan,ms):
        self.expchanged(chan, ms)
        ms = c_long(ms)
        chan = c_long(chan)
        yield self.wmdll.SetExposureNum(chan,1,  ms)

        
    @setting(15, "Set Lock State", state = 'b')
    def setLockState(self,c,state):
        state = c_bool(state)
        yield self.wmdll.SetDeviationMode(state)
               
    @setting(11, "Set Output Voltage", mV = ['v'])
    def setOutputVoltage(self,c,mV):
        yield self.wmdll.SetDeviationSignalNum(self.chanNum, mV)       
        
    @setting(14, "Set Switcher Mode", mode = 'b')
    def setSwitcherMode(self, c, mode):
        mode = c_long(mode)
        yield self.wmdll.SetSwitcherMode(mode)      
        
    @setting(13, "Set Switcher Signal State", chan = 'i', state = 'b')
    def setSwitcherState(self, c, chan, state):
        chan = c_long(chan)
        state = c_long(state)
        yield self.wmdll.SetSwitcherSignalStates(chan, state, self.l)
        

        

#####Set Functions

    @setting(26, "Get Amplitude", chan = 'i', returns = 'v')
    def getExp(self, c, chan): 
        chan = c_long(chan)
        amp = yield self.wmdll.GetAmplitudeNum(chan, c_long(2), self.l) 
        returnValue(amp)

    @setting(23, "Get Exposure", chan = 'i', returns = 'i')
    def getExp(self, c, chan): 
        chan = c_long(chan)
        exp = yield self.wmdll.GetExposureNum(chan ,1,self.l) 
        returnValue(exp)

    @setting(20,"Get Frequency", chan = 'i', returns = 'v')
    def getFrequency(self, c, chan):
        chan = c_long(chan)
        freq = yield self.wmdll.GetFrequencyNum(chan,self.d)
        self.freqSignal = freq
        self.freqchanged(int(chan),freq)
        returnValue(freq)
        
    @setting(24, "Get Lock State")
    def getLockState(self):
        state = self.wmdll.GetDeviationMode(self.b)
        returnValue(state)
        
    @setting(21,"Get Output Voltage", chan = 'i', returns = 'v')
    def getOutputVoltage(self, c, chan):
        chan = c_long(chan)
        volts = yield self.wmdll.GetDeviationSignalNum(chan,self.d)
        returnValue(volts)  
        
    @setting(27, "Get Switcher Mode", returns = 'b')
    def getSwitcherMode(self, c):
        state = self.wmdll.GetSwitcherMode(self.l)
        returnValue(state)
    
    @setting(25, "Get Switcher Signal State", chan = 'i', returns = 'b')
    def getSwitcherState(self, c, chan):
        chan = c_long(chan)
        use = c_long(0)
        state = self.wmdll.GetSwitcherSignalStates(chan, pointer(use), pointer(show))
        returnValue(use)
        

    

        
if __name__ == "__main__":
    from labrad import util
    util.runServer(MultiplexerServer())
    
    