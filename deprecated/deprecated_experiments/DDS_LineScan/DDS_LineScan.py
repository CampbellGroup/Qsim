import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import time

class DDS_LineScan(QsimExperiment):

    name = 'DDS LineScan'
    exp_parameters = []
    exp_parameters.append(('DDS_line_scan', 'DDS_Frequencies'))
    exp_parameters.append(('DDS_line_scan', 'Collection_Time'))
    exp_parameters.append(('DDS_line_scan', 'Center_Frequency'))
    exp_parameters.append(('DDS_line_scan', 'Power'))

    def initialize(self, cxn, context, ident):

        self.pmt = cxn.normalpmtflow
        self.pulser = cxn.pulser
        self.init_mode = self.pmt.getcurrentmode()
        self.init_gate_time = self.pmt.get_time_length()
        self.init_freq = self.pulser.frequency('369DP')
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('Frequency', 'Counts')
        self.setup_grapher('DDS LineScan')
        self.pmt.set_mode('Normal')
        self.gate_time = self.p.DDS_line_scan.Collection_Time
        self.center_freq = self.p.DDS_line_scan.Center_Frequency
        self.power = self.p.DDS_line_scan.Power
        self.pmt.set_time_length(self.gate_time)
        self.pulser.amplitude('369DP', self.power)
        self.x_values = self.get_scan_list(self.p.DDS_line_scan.DDS_Frequencies, units='MHz')

        for i, x_point in enumerate(self.x_values):

            should_break = self.update_progress(i/float(len(self.x_values)))
            if should_break:
                self.finalize(cxn, context)
                break

            self.pulser.frequency('369DP', U(x_point, 'MHz'))
            time.sleep(self.gate_time['s'])
            counts = self.pmt.get_next_counts('ON', 1, False)[0]
            if counts:
                self.dv.add(2*(x_point - self.center_freq['MHz']), counts) # Since Double passed factor of 2 added

    def finalize(self, cxn, context):
        self.pulser.frequency('369DP', self.init_freq)
        self.pmt.set_mode(self.init_mode)
        self.pmt.set_time_length(self.init_gate_time)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DDS_LineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
