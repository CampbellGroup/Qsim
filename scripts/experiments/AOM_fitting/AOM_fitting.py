import labrad
from labrad.units import WithUnit as U
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time
import numpy as np

__scriptscanner_name__ = 'AOM_fitting'  # this should match the class name
class AOM_fitting(QsimExperiment):
    '''
    perform DDS line scan with AOM only, fit to a high degree polynomial,
    use fit to flatten laser power profile as a function of AOM frequency so that
    line scans come out symmetric.
    '''
    name = 'AOM Fitting'

    exp_parameters = []
    exp_parameters.append(('AOM_fitting', 'DDS_Frequencies'))
    exp_parameters.append(('AOM_fitting', 'Collection_Time'))
    exp_parameters.append(('AOM_fitting', 'Center_Frequency'))
    exp_parameters.append(('AOM_fitting', 'Power'))

    def initialize(self, cxn, context, ident):

        self.reg = cxn.registry
        self.reg.cd(['','settings'])
        self.pmt = cxn.normalpmtflow
        self.pulser = cxn.pulser
        self.init_mode = self.pmt.getcurrentmode()
        self.init_gate_time = self.pmt.get_time_length()
        self.init_freq = self.pulser.frequency('369')
        self.ident = ident
        self.intensity = []
        self.delta_freq = []
        self.fitIntensity = []

    def run(self, cxn, context):

        self.setup_datavault('Frequency', 'Counts')
        self.setup_grapher('AOM Fitting')
        self.pmt.set_mode('Normal')
        self.gate_time = self.p.AOM_fitting.Collection_Time
        self.center_freq = self.p.AOM_fitting.Center_Frequency
        self.power = self.p.AOM_fitting.Power
        self.pmt.set_time_length(self.gate_time)
        self.pulser.amplitude('369', self.power)
        self.x_values = self.get_scan_list(self.p.AOM_fitting.DDS_Frequencies, units='MHz')


        tmp_counts = []
        for i, x_point in enumerate(self.x_values):

            should_break = self.update_progress(i / float(len(self.x_values)))
            if should_break:
                self.finalize(cxn, context)
                break

            self.pulser.frequency('369', U(x_point, 'MHz'))
            time.sleep(self.gate_time['s'])
            counts = self.pmt.get_next_counts('ON', 1, False)[0]
            self.intensity.append(counts)
            self.delta_freq.append(x_point - self.center_freq['MHz'])
            if counts:
                self.dv.add(2 * (x_point - self.center_freq['MHz']), counts)  # Since Double passed factor of 2 added
                tmp_counts.append(counts)

        self.fit_parameters = self.fit_profile(self.delta_freq, self.intensity/np.max(tmp_counts))
        self.reg.set('AOM_calibration', self.fit_parameters)
        self.setup_datavault('Fit', 'Counts')
        self.setup_grapher('AOM Fitting')
        for n in range(len(self.x_values)):
            self.fitIntensity.append(np.polyval(self.fit_parameters, self.delta_freq[n]))
            self.dv.add(2*(self.delta_freq[n]), np.max(tmp_counts)*self.fitIntensity[n])


    def fit_profile(self, x, y):
        fit = np.polyfit(x, y, 20)
        return fit


    def finalize(self, cxn, context):
        self.pulser.frequency('369', self.init_freq)
        self.pmt.set_mode(self.init_mode)
        self.pmt.set_time_length(self.init_gate_time)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = AOM_fitting(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)



