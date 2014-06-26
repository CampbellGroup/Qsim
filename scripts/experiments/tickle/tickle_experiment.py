import labrad
from Qsim.abstractdevices.script_scanner.scan_methods import experiment
from twisted.internet import task
from twisted.internet.defer import returnValue
import time

class ticklescan(experiment):
    
    name = 'Tickle Scan'
    
    required_parameters =[('ticklescan', 'amplitude'), ('ticklescan', 'frequency'), ('ticklescan', 'amplitude'), ('ticklescan', 'offset')]
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Tickle Scan')
        self.cxnwlm = labrad.connect('169.232.156.230', name = 'Tickle Scan')
        self.dv = self.cxn.data_vault
        self.rg = self.cxnwlm.rigol_dg1022_server      
        self.pv = self.cxn.parametervault
        self.pmt = cxn.arduinocounter
        self.chan = 1
    
    def run(self, cxn, context):
        
        amplitude = self.pv.get_parameter('ticklescan', 'amplitude')
        frequency = self.pv.get_parameter('ticklescan','frequency')                
        offset = self.pv.get_parameter('ticklescan', 'offset')
        minval = int(frequency[0]['Hz'])
        maxval = int(frequency[1]['Hz'])
        numberofsteps = int(frequency[2])
        stepsize = int((float(maxval) - minval)/(numberofsteps- 1))
        
        
        self.dv.cd('Tickle Scan', True)
        self.dv.new('Tickle Scan',[('freq', 'num')], [('kilocounts/sec','','num')])
        window_name = 'V'
        
        self.dv.add_parameter('Window', window_name)
        self.dv.add_parameter('plotLive', True)
        
        self.dv.add_parameter('amplitude', amplitude)
        self.dv.add_parameter('frequency', frequency)
        self.dv.add_parameter('offset', offset)
        xvalues = range(minval,maxval + 1,stepsize)
        self.rg.query_device
        self.rg.set_output(True)
 #       from twisted.internet import reactor
        for i, freq in enumerate(xvalues):
                should_stop = self.pause_or_stop()
                if should_stop: break
                self.rg.apply_wave_form(self.chan, 'sine', freq, amplitude, offset)
                counts = self.pmt.get_current_counts()    
                time.sleep(.1)
#                counts = yield task.deferLater(0.1, self.getcounts, self)
                self.dv.add(freq, counts)
                progress = 100*float(i)/numberofsteps
                self.sc.script_set_progress(self.ident, progress)
        self.rg.set_output(False)
        
    def getcounts(self):
        counts = self.pmt.get_current_counts()
        returnValue(counts)
        
    def finalize(self, cxn, context):
        self.cxn.disconnect()
        
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ticklescan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)