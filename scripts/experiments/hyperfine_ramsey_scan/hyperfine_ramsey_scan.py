import labrad
from Qsim.scripts.pulse_sequences.hyperfine_ramsey_scan import hyperfine_ramsey_scan as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import time
import numpy as np


class hyperfine_ramsey_scan(QsimExperiment):

    name = 'Hyperfine Ramsey Scan'

    exp_parameters = []
    exp_parameters.append(('Delaystagescan', 'scan'))
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('ShelvingDopplerCooling', 'doppler_counts_threshold'))
    exp_parameters.append(('MLStateDetection', 'repititions'))
    exp_parameters.append(('MLStateDetection', 'points_per_histogram'))
    exp_parameters.append(('MLStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('bf_fluorescence', 'crop_start_time'))
    exp_parameters.append(('bf_fluorescence', 'crop_stop_time'))
    exp_parameters.append(('MLStateDetection', 'repititions'))
    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))
    exp_parameters.append(('Transitions', 'qubit_0'))
    exp_parameters.append(('Transitions', 'qubit_plus'))
    exp_parameters.append(('Transitions', 'qubit_minus'))
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.prob_ctx = self.dv.context()
        self.hist_ctx = self.dv.context()
        self.chan = 2
        self.keithley = self.cxn.keithley_2230g_server
        self.keithley.select_device(0)
        self.ds = self.cxn.ds1054_scope_server

    def run(self, cxn, context):
        self.setup_prob_datavault()
        self.voltages = self.get_scan_list(self.p.Delaystagescan.scan, 'V')
        self.init_volt = self.voltages[0]
        self.p['Modes.state_detection_mode'] == 'Standard'
        for i, volt in enumerate(self.voltages):
            self.keithley.gpib_write('APPLy CH2,' + str(volt) + 'V')
            tracer_volt = self.ds.measurevpp(1)
            tracer_volt = float(tracer_volt[:-1])
            time.sleep(1)
            self.program_pulser(sequence)
            [counts10, counts11, counts01] = self.run_sequence(max_runs=300, num=3)
            self.plot_prob(volt, counts10, counts11, counts01, tracer_volt)
            should_break = self.update_progress(i/float(len(self.voltages)))
            if should_break:
                break

    def setup_prob_datavault(self):
        self.dv.cd(['', 'hyperfine_ramsey_scan'], True, context=self.prob_ctx)

        self.dataset_prob = self.dv.new('hyperfine_ramsey_scan', [('run', 'prob')],
                                        [('Prob', 'fringe10', 'num'),
                                         ('Prob', 'fringe11', 'num'),
                                         ('Prob', 'fringe01', 'num'),
                                         ('Voltage', 'tracer beam', 'volts')],
                                        context=self.prob_ctx)
        self.grapher.plot(self.dataset_prob, 'ML_decoherence', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.prob_ctx)

    def plot_prob(self, voltage, counts10, counts11, counts01, tracer_volt):
        prob10 = self.get_pop(counts10)
        prob11 = self.get_pop(counts11)
        prob01 = self.get_pop(counts01)
        self.dv.add(voltage, prob10/0.66, prob11/0.66, prob01/0.66, tracer_volt, context=self.prob_ctx)

    def finalize(self, cxn, context):
        self.keithley.gpib_write('Apply CH2,' + str(self.init_volt) + 'V')



if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = hyperfine_ramsey_scan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
