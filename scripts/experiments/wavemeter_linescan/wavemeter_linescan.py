import labrad
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods \
    import experiment


class wavemeter_linescan(experiment):

    name = 'Wavemeter Line Scan'

    exp_parameters = []
    exp_parameters.append(('wavemeterscan', 'lasername'))

    exp_parameters.append(('wavemeterscan', 'Port_369'))
    exp_parameters.append(('wavemeterscan', 'Port_399'))
    exp_parameters.append(('wavemeterscan', 'Port_935'))

    exp_parameters.append(('wavemeterscan', 'Center_Frequency_369'))
    exp_parameters.append(('wavemeterscan', 'Center_Frequency_399'))
    exp_parameters.append(('wavemeterscan', 'Center_Frequency_935'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.laser = self.parameters.wavemeterscan.lasername

        if self.laser == '369':
            self.port = self.parameters.wavemeterscan.Port_369
            self.centerfrequency = \
                self.parameters.wavemeterscan.Center_Frequency_369

        elif self.laser == '399':
            self.port = self.parameters.wavemeterscan.Port_399
            self.centerfrequency = \
                self.parameters.wavemeterscan.Center_Frequency_399

        elif self.laser == '935':
            self.port = self.parameters.wavemeterscan.Port_935
            self.centerfrequency = \
                self.parameters.wavemeterscan.Center_Frequency_935

        self.cxn = labrad.connect(name='Wavemeter Line Scan')
        self.cxnwlm = labrad.connect('10.97.112.2',
                                     name='Wavemeter Scan', password='lab')
        self.wm = self.cxnwlm.multiplexerserver
        self.dv = self.cxn.data_vault
        self.grapher = self.cxn.grapher
        self.pmt = self.cxn.normalpmtflow

    def run(self, cxn, context):

        self.dv.cd('Wavemeter Line Scan', True)
        dataset = self.dv.new('Wavemeter Line Scan', [('freq', 'Hz')],
                              [('', 'Amplitude', 'kilocounts/sec')])
        self.grapher.plot(dataset, 'spectrum', False)

        self.dv.add_parameter('Frequency', self.centerfrequency)
        self.dv.add_parameter('Laser', self.laser)

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
        absfreq = WithUnit(float(self.wm.get_frequency(self.port)), 'THz')
        self.currentfreq = absfreq - self.centerfrequency

    def finalize(self, cxn, context):
        self.cxn.disconnect()
        self.cxnwlm.disconnect()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = wavemeter_linescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
