import labrad
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
import time

class M2pumpmonitor(experiment):
    
    name = 'M2 Pump Monitor'

    exp_parameters = []
    exp_parameters.append(('M2pumpmonitor', 'reading'))
    exp_parameters.append(('M2pumpmonitor', 'measuretime'))
    exp_parameters.append(('M2pumpmonitor', 'sampletime'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.cxn = labrad.connect(name = 'M2 Pump Monitor')
        self.grapher = self.cxn.Grapher
        self.pmp = self.cxn.m2pump
        self.dv = self.cxn.data_vault
        self.p = self.parameters
        self.inittime = time.time()

    def run(self, cxn, context):
        
        '''
        Main loop 
        '''

        self.setup_datavault()
        while (time.time() - self.inittime) <= self.p.M2pumpmonitor.measuretime['s']:
            should_stop = self.pause_or_stop()
            if should_stop: break
            if self.p.M2pumpmonitor.reading == 'current':
                current = self.pmp.read_current()
                self.dv.add(time.time() - self.inittime, current)
            elif self.p.M2pumpmonitor.reading == 'power':
                power = self.pmp.read_power()
                self.dv.add(time.time() - self.inittime, power['W'])
            progress = 100*float(time.time() - self.inittime)/self.p.M2pumpmonitor.measuretime['s']
            if progress >= 100.0: progress = 100.0
            self.sc.script_set_progress(self.ident, progress)
            time.sleep(self.p.M2pumpmonitor.sampletime['s'])

    def setup_datavault(self):

        '''
        Adds parameters to datavault and parameter vault
        '''
        
        self.dv.cd('M2 Pump Monitor', True)
        name = self.dv.new('M2 Pump Monitor',[('time', 's')], [(self.p.M2pumpmonitor.reading,'','num')])
        window_name = ['M2 Pump Monitor']
        self.dv.add_parameter('Window', window_name)
        self.dv.add_parameter('plotLive', True)
        self.dv.add_parameter('reading type', self.p.M2pumpmonitor.reading)
        self.grapher.plot(name,'Pump Monitor',False)

    def finalize(self, cxn, context):
        self.cxn.disconnect() 
        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = M2pumpmonitor(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
