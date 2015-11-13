import labrad
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import returnValue
from labrad.units import WithUnit
import time
import socket

class ticklescan(experiment):
    
    name = 'Tickle Scan'

    exp_parameters = []
    exp_parameters.append(('ticklescan', 'amplitude'))
    exp_parameters.append(('ticklescan', 'frequency'))
    exp_parameters.append(('ticklescan', 'average'))
    exp_parameters.append(('ticklescan', 'offset'))
    exp_parameters.append(('ticklescan', 'waveform'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxn = labrad.connect(name = 'Tickle Scan')
        self.cxnwlm = labrad.connect('10.97.112.2', name = socket.gethostname() + " Tickle Scan")
        self.dv = self.cxn.data_vault
        self.rg = self.cxnwlm.rigol_dg1022a_server      
        self.pmt = self.cxn.normalpmtflow
	self.p = self.parameters
        self.chan = 1
        self.rg.select_device(0)   
    
    def run(self, cxn, context):
        
        '''
        Main loop 
        '''
	self.set_scannable_parameters()
	self.setup_datavault()
        self.rg.output(self.chan, True)
	time.sleep(0.1)
        self.rg.apply_waveform(self.p.ticklescan.waveform, self.frequency[0], self.amplitude, self.offset, self.chan)
	time.sleep(1)
        for i, freq in enumerate(self.xvalues):
                should_stop = self.pause_or_stop()
                if should_stop: break
                self.rg.frequency(self.chan, WithUnit(freq, 'Hz'))  
		time.sleep(0.1)
                counts = self.pmt.get_next_counts('ON', self.average, True)
                time.sleep(0.1)
                self.dv.add(freq, counts)
                progress = 100*float(i)/self.numberofsteps
                self.sc.script_set_progress(self.ident, progress)
        self.rg.output(self.chan, False)
        self.rg.frequency(self.chan, self.frequency[0])

    def set_scannable_parameters(self):

	'''
	gets parameters, called in run so scan works
	'''

        self.amplitude = self.p.ticklescan.amplitude
        self.frequency = self.p.ticklescan.frequency  
        self.offset = self.p.ticklescan.offset 
        self.average = int(self.p.ticklescan.average)
        self.minval = self.p.ticklescan.frequency[0]['Hz']
        self.maxval = self.p.ticklescan.frequency[1]['Hz']
        self.numberofsteps = int(self.p.ticklescan.frequency[2])
        self.stepsize = int((float(self.maxval) - self.minval)/(self.numberofsteps- 1))   
        self.xvalues = range(int(self.minval), int(self.maxval + 1),self.stepsize)

    def setup_datavault(self):

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
        
    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()
        
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ticklescan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
