import labrad
from Qsim.scripts.pulse_sequences.shelving_fidelity import shelving_fidelity as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np
from labrad.units import WithUnit as U


class shelving_fidelity(QsimExperiment):
    """
    shelving fidelity with experimental checks
    """

    name = 'Shelving Fidelity'

    exp_parameters = []
    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))
    exp_parameters.append(('MicrowaveInterogation', 'repititions'))
    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))

    exp_parameters.remove(('MicrowaveInterogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        qubit = self.p.Line_Selection.qubit

        if qubit == 'qubit_0':
            pi_time = self.p.Pi_times.qubit_0

        elif qubit == 'qubit_plus':
            pi_time = self.p.Pi_times.qubit_plus

        elif qubit == 'qubit_minus':
            pi_time = self.p.Pi_times.qubit_minus

        self.p['MicrowaveInterogation.duration'] = pi_time
        self.p['MicrowaveInterogation.detuning'] = U(0.0, 'kHz')
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.setup_prob_datavault()
        i = 0
        self.program_pulser(sequence)

        while True:
            i += 1
            [counts_doppler_bright, counts_bright, counts_doppler_dark, counts_dark] = self.run_sequence(max_runs=250, num=4)
            print counts_doppler_bright, counts_bright, counts_doppler_dark, counts_dark
            bright_errors = np.where(counts_doppler_bright <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            counts_bright = np.delete(counts_bright, bright_errors)

            dark_errors = np.where(counts_doppler_dark <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            counts_dark = np.delete(counts_dark, dark_errors)

            print 'Dark Doppler Errors:', len(dark_errors[0])
            print 'Bright Doppler Errors:', len(bright_errors[0])
            print 'Mean Doppler Counts:', np.mean(counts_doppler_bright)

            hist_bright = self.process_data(counts_bright)
            hist_dark = self.process_data(counts_dark)

            self.plot_hist(hist_bright, folder_name='Shelving_Histogram')
            self.plot_hist(hist_dark, folder_name='Shelving_Histogram')

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
        self.dv.cd(['', 'shelving_fidelity'], True)

        self.dataset_prob = self.dv.new('shelving_fidelity', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')])
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

    def plot_prob(self, num, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright,
                    prob_bright - prob_dark)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = shelving_fidelity(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
