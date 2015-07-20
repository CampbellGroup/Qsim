import labrad
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import returnValue
from labrad.units import WithUnit
import time
import socket

class ticklescan(experiment):
    
    name = 'Tickle Scan'
    
    required_parameters =[('ticklescan', 'amplitude'), ('ticklescan', 'frequency'), ('ticklescan', 'average'), ('ticklescan', 'offset')]
    
    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxn = labrad.connect(name = 'Tickle Scan')
        self.cxnwlm = labrad.connect('10.97.112.2', name = socket.gethostname() + " Tickle Scan")
        self.dv = self.cxn.data_vault
        self.rg = self.cxnwlm.rigol_dg1022a_server      
        self.pv = self.cxn.parametervault
        self.pmt = self.cxn.normalpmtflow
        self.chan = 1

        '''
        Sets up data vault and parameter vault
        '''
        self.rg.select_device(0)   
        self.amplitude = self.pv.get_parameter('ticklescan', 'amplitude')
        self.frequency = self.pv.get_parameter('ticklescan','frequency')  
             
        self.offset = self.pv.get_parameter('ticklescan', 'offset')
        self.average = int(self.pv.get_parameter('ticklescan', 'average'))
        self.minval = int(self.frequency[0]['Hz'])
        self.maxval = int(self.frequency[1]['Hz'])
        self.numberofsteps = int(self.frequency[2])
        self.stepsize = int((float(self.maxval) - self.minval)/(self.numberofsteps- 1))   
        self.rg.apply_waveform('sine', self.frequency[0], self.amplitude, self.offset, self.chan)
        
        '''
        Adds parameters to datavault and parameter vault
        '''
        
        self.dv.cd('Tickle Scan', True)
        self.dv.new('Tickle Scan',[('freq', 'num')], [('kilocounts/sec','','num')])
        window_name = ['Tickle']
        self.dv.add_parameter('Window', window_name)
        self.dv.add_parameter('plotLive', True)
        self.dv.add_parameter('amplitude', self.amplitude)
        self.dv.add_parameter('frequency', self.frequency)
        self.dv.add_parameter('offset', self.offset)
        self.dv.add_parameter('average', self.average)
        self.xvalues = range(self.minval, self.maxval + 1,self.stepsize)

    
    def run(self, cxn, context):
        
        '''
        Main loop 
        '''
        self.rg.output(self.chan, True)
        for i, freq in enumerate(self.xvalues):
                should_stop = self.pause_or_stop()
                if should_stop: break
                self.rg.frequency(self.chan, WithUnit(freq, 'Hz'))  
                counts = self.pmt.get_next_counts('ON', self.average, True)
                time.sleep(0.1)
                self.dv.add(freq, counts)
                progress = 100*float(i)/self.numberofsteps
                self.sc.script_set_progress(self.ident, progress)
        self.rg.output(self.chan, False)
        self.rg.frequency(self.chan, self.frequency[0])
        
    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()
        
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ticklescan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
