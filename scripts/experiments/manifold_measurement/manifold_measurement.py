import labrad
from Qsim.scripts.pulse_sequences.manifold_measurement import manifold_measurement as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np
from labrad.units import WithUnit as U


class manifold_measurement(QsimExperiment):
    """
    Experiment based on fidelity tweak up to measure
    the S, F state manifold preparation and readout fidelity
    """

    name = 'Manifold Measurement'

    exp_parameters = []
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.append(('StateDetection', 'doppler_counts_threshold'))
    exp_parameters.append(('StateDetection', 'points_per_histogram'))
    exp_parameters.extend(sequence.all_required_parameters())

    
    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_prob_datavault()
        i = 0
        self.program_pulser(sequence)
        while True:
            i += 1
            counts = self.run_sequence(max_runs=250)
            counts_doppler_bright = counts[0::4]
                
            bright_errors = np.where(counts_doppler_bright <= self.p.StateDetection.doppler_counts_threshold)
            counts_bright = counts[1::4]
            counts_bright = np.delete(counts_bright, bright_errors)
            counts_doppler_dark = counts[2::4]
            dark_errors = np.where(counts_doppler_dark <= self.p.StateDetection.doppler_counts_threshold)
            counts_dark = counts[3::4]
            counts_dark = np.delete(counts_dark, dark_errors)
            print dark_errors, bright_errors

            if i % self.p.StateDetection.points_per_histogram == 0:
                hist_bright = self.process_data(counts_bright)
                hist_dark = self.process_data(counts_dark)
                self.plot_hist(hist_bright, folder_name='manifold_data_bright')
                self.plot_hist(hist_dark, folder_name='manifold_data_dark')
            self.plot_prob(i, counts_bright, counts_dark)
            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                self.program_pulser(sequence)

    def setup_prob_datavault(self):
        self.dv.cd(['', 'manifold_measurement'], True)

        self.dataset_prob = self.dv.new('manifold_measurement', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num')])
        self.grapher.plot(self.dataset_prob, 'Manifolds', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

    def plot_prob(self, num, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = manifold_measurement(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
