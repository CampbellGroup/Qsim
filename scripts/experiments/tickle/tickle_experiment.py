import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit
import time


class ticklescan(QsimExperiment):

    name = 'Tickle Scan'

    exp_parameters = []
    exp_parameters.append(('ticklescan', 'amplitude'))
    exp_parameters.append(('ticklescan', 'frequency_scan'))
    exp_parameters.append(('ticklescan', 'average'))
    exp_parameters.append(('ticklescan', 'offset'))
    exp_parameters.append(('ticklescan', 'waveform'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.rg = self.cxn.dg1022_rigol_server
        self.pmt = self.cxn.normalpmtflow
        self.chan = 1

    def run(self, cxn, context):

        '''
        Main loop
        '''

        self.setup_datavault('Frequency', 'kCounts/sec')
        self.setup_grapher('tickle_scan')
        self.set_scannable_parameters()
        self.x_values = self.get_scan_list(self.p.ticklescan.frequency_scan, units='Hz')
        self.rg.set_output(self.chan, True)
        self.rg.applywaveform(self.p.ticklescan.waveform, WithUnit(self.x_values[0], 'Hz'),
                              self.amplitude, self.offset, self.chan)
        time.sleep(1)

        for i, freq in enumerate(self.x_values):
            should_break = self.update_progress(i / float(len(self.x_values)))
            if should_break:
                break

            self.rg.frequency(self.chan, WithUnit(freq, 'Hz'))
            counts = self.pmt.get_next_counts('ON', self.average, True)
            self.dv.add(freq, counts)

    def set_scannable_parameters(self):

        '''
        gets parameters, called in run so scan works
        '''

        self.amplitude = self.p.ticklescan.amplitude
        self.offset = self.p.ticklescan.offset
        self.average = int(self.p.ticklescan.average)

    def finalize(self, cxn, context):
        self.rg.set_output(self.chan, False)
        self.rg.frequency(self.chan, WithUnit(self.x_values[0], 'Hz'))


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ticklescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
