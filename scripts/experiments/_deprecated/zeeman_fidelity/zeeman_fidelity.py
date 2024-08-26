import labrad
from Qsim.scripts.pulse_sequences.zeeman_fidelity import zeeman_fidelity as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np
from labrad.units import WithUnit as U


class zeeman_fidelity(QsimExperiment):

    name = 'Zeeman Fidelity'
    exp_parameters = []
    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))


    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.setup_prob_datavault()
        i = 0
        self.program_pulser(sequence)
        while True:
            i += 1
            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                self.program_pulser(sequence)

            [counts_doppler_bright, counts_bright, counts_doppler_dark, counts_dark] = self.run_sequence(max_runs=250, num=4)
            bright_errors = np.where(counts_doppler_bright <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            counts_bright = np.delete(counts_bright, bright_errors)

            dark_errors = np.where(counts_doppler_dark <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            counts_dark = np.delete(counts_dark, dark_errors)

            print 'Dark Doppler Errors:', len(dark_errors[0])
            print 'Bright Doppler Errors:', len(bright_errors[0])
            print 'Mean Doppler Counts:', np.mean(counts_doppler_bright)
            print counts_bright
            print counts_dark
            hist_bright = self.process_data(counts_bright)
            hist_dark = self.process_data(counts_dark)

            self.plot_hist(hist_bright, folder_name='Zeeman_Histogram')
            self.plot_hist(hist_dark, folder_name='Zeeman_Histogram')

            self.plot_prob(i, counts_bright, counts_dark)

    def setup_prob_datavault(self):
        self.dv_context = self.dv.context()
        self.dv.cd(['', 'zeeman_fidelity'], True, context=self.dv_context)

        self.dataset_prob = self.dv.new('zeeman_fidelity', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')], context=self.dv_context)
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.dv_context)

    def plot_prob(self, num, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright,
                    prob_bright - prob_dark, context=self.dv_context)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = zeeman_fidelity(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
