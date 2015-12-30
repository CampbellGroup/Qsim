import labrad
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
class wavemeter_linescan(experiment):
    
    name = 'Wavemeter Line Scan'
    
    required_parameters = [('frequencycenter', 'lasername')]
    
    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.laserport = 8
        self.cxn = labrad.connect(name = 'Wavemeter Line Scan')
        self.cxnwlm = labrad.connect('10.97.112.2', name = 'Wavemeter Scan')
        self.wm = self.cxnwlm.multiplexerserver  
        self.dv = self.cxn.data_vault      
        self.pv = self.cxn.parametervault
        self.pmt = self.cxn.normalpmtflow
        
    def run(self, cxn, context):
        
        self.centerfrequency = self.pv.get_parameter('wavemeterscan','frequencycenter')     
        self.laser = self.pv.get_parameter('wavemeterscan','lasername')           
        
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
        self.currentfreq = WithUnit(float("%.6f" % self.wm.get_frequency(self.laserport)) - self.centerfrequency, 'THz')
        
    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = wavemeter_linescan(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




