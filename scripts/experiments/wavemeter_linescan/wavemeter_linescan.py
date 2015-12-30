import labrad
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
class wavemeter_linescan(experiment):
    
    name = 'Wavemeter Line Scan'
    
    exp_parameters = []
    exp_parameters.append(('wavemeterscan', 'lasername'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cxn = labrad.connect(name = 'Wavemeter Line Scan')
        self.cxnwlm = labrad.connect('10.97.112.2', name = 'Wavemeter Scan')
        self.wm = self.cxnwlm.multiplexerserver  
        self.dv = self.cxn.data_vault      
        self.pmt = self.cxn.normalpmtflow
        self.laserdict = {'369':5,'935':6,'399':8}
        self.centerdict = {'369':WithUnit(405.645745,'THz'),'399':WithUnit(751.527140,'THz'),'935':WithUnit(320.571975,'THz')}
        
    def run(self, cxn, context):
        
        self.laser = self.parameters.wavemeterscan.lasername
        self.laserport = self.laserdict[self.laser]       
        self.centerfrequency = self.centerdict[self.laser]
        
        self.dv.cd('Wavemeter Line Scan', True)
        self.dv.new('Wavemeter Line Scan',[('freq', 'Hz')], [('', 'Amplitude','kilocounts/sec')])
        window_name = ['Wavemeter Line Scan']

        self.dv.add_parameter('Window', window_name)
        self.dv.add_parameter('plotLive', True)
        self.dv.add_parameter('Frequency', self.centerfrequency)

        self.currentfreq = self.currentfrequency()
        tempdata = []
        while True:
            should_stop = self.pause_or_stop()
            if should_stop: 
                tempdata.sort()
                self.dv.add(tempdata)
                break
            counts = self.pmt.get_next_counts('ON', 1, False)
            self.currentfrequency()
            if self.currentfreq and counts:
                tempdata.append([self.currentfreq['GHz'], counts])

            
            
            
    def currentfrequency(self):
        self.currentfreq = WithUnit(float(self.wm.get_frequency(self.laserport)), 'THz') - self.centerfrequency
        
    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = wavemeter_linescan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




