import labrad
from Qsim.abstractdevices.script_scanner.scan_methods import experiment
from twisted.internet.defer import returnValue
import time

class ticklescan(experiment):
    
    name = 'Tickle Scan'
    
    required_parameters =[('ticklescan', 'amplitude'), ('ticklescan', 'frequency'), ('ticklescan', 'average'), ('ticklescan', 'offset')]
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Tickle Scan')
        self.cxnwlm = labrad.connect('10.97.112.2', name = 'Tickle Scan')
        self.dv = self.cxn.data_vault
        self.rg = self.cxnwlm.rigol_dg1022_server      
        self.pv = self.cxn.parametervault
        self.pmt = cxn.arduino_counter
        self.chan = 1
    
    def run(self, cxn, context):
        
        amplitude = self.pv.get_parameter('ticklescan', 'amplitude')
        frequency = self.pv.get_parameter('ticklescan','frequency')                
        offset = self.pv.get_parameter('ticklescan', 'offset')
        average = int(self.pv.get_parameter('ticklescan', 'average'))
        minval = int(frequency[0]['Hz'])
        maxval = int(frequency[1]['Hz'])
        numberofsteps = int(frequency[2])
        stepsize = int((float(maxval) - minval)/(numberofsteps- 1))
        
        
        self.dv.cd('Tickle Scan', True)
        self.dv.new('Tickle Scan',[('freq', 'num')], [('kilocounts/sec','','num')])
        window_name = ['Tickle']
        
        self.dv.add_parameter('Window', window_name)
        self.dv.add_parameter('plotLive', True)
        
        self.dv.add_parameter('amplitude', amplitude)
        self.dv.add_parameter('frequency', frequency)
        self.dv.add_parameter('offset', offset)
        self.dv.add_parameter('average', average)
        xvalues = range(minval,maxval + 1,stepsize)
        self.rg.query_device
        self.rg.set_output(True)
        for i, freq in enumerate(xvalues):
                should_stop = self.pause_or_stop()
                if should_stop: break
                self.rg.apply_wave_form(self.chan, 'sine', freq, amplitude, offset)
                counts = 0   
                for j in range(average):    
                    counts = self.pmt.get_current_counts() + counts
                    time.sleep(0.1)
                counts = counts/average
                self.dv.add(freq, counts)
                progress = 100*float(i)/numberofsteps
                self.sc.script_set_progress(self.ident, progress)
        
    def getcounts(self):
        counts = self.pmt.get_current_counts()
        returnValue(counts)
        
    def finalize(self, cxn, context):
        self.rg.set_output(False)
        self.cxn.disconnect()
        self.cxnwlm.disconnect()
        
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ticklescan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
