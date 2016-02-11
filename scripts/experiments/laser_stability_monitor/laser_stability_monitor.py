import labrad
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import returnValue
from labrad.units import WithUnit
import time
import socket

class lasermonitor(experiment):
    
    name = 'Laser Monitor'

    exp_parameters = []
    exp_parameters.append(('lasermonitor', 'lasers'))
    exp_parameters.append(('lasermonitor', 'measuretime'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxn = labrad.connect(name = 'Laser Monitor')
        self.cxnwlm = labrad.connect('10.97.112.2', name = socket.gethostname() + " Laser Monitor")
        self.grapher = self.cxn.grapher
	self.wlm = self.cxnwlm.multiplexerserver
        self.dv = self.cxn.data_vault
	self.p = self.parameters
	self.inittime = time.time()
	self.initfreq = self.wlm.get_frequency(int(self.p.lasermonitor.lasers[-1]))

    def run(self, cxn, context):
        
        '''
        Main loop 
        '''

	self.setup_datavault()
	while (time.time() - self.inittime) <= self.p.lasermonitor.measuretime['s']:
		should_stop = self.pause_or_stop()
                if should_stop: break
		freq = self.wlm.get_frequency(int(self.p.lasermonitor.lasers[-1]))
		self.dv.add(time.time() - self.inittime, 1e6*(self.initfreq - freq))
                progress = 100*float(time.time() - self.inittime)/self.p.lasermonitor.measuretime['s']
                self.sc.script_set_progress(self.ident, progress)
		

    def setup_datavault(self):

        '''
        Adds parameters to datavault and parameter vault
        '''
        
        self.dv.cd('Laser Monitor', True)
        name = self.dv.new('Laser Monitor',[('time', 's')], [('freq','','num')])
        window_name = ['Laser Monitor']
        self.dv.add_parameter('Window', window_name)
        self.dv.add_parameter('plotLive', True)
        self.dv.add_parameter('lasers', self.p.lasermonitor.lasers)
        self.grapher.plot(name, 'Laser Monitor', False)

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()
        
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = lasermonitor(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
