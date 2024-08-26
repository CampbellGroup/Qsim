import labrad
from Qsim.scripts.pulse_sequences.ML_decoherence import ML_decoherence as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U


class ML_decoherence(QsimExperiment):

    name = 'ML_decoherence'

    exp_parameters = []
    exp_parameters.append(('ML_decoherence', 'ML_time_scan'))
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('ShelvingDopplerCooling', 'doppler_counts_threshold'))
    exp_parameters.append(('MLStateDetection', 'repititions'))
    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('ML_interogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.prob_ctx = self.dv.context()
        self.hist_ctx = self.dv.context()

    def run(self, cxn, context):

        self.setup_prob_datavault()
        self.times = self.get_scan_list(self.p.ML_decoherence.ML_time_scan, 'us')
        self.p['Modes.state_detection_mode'] = 'Standard'
        for i, duration in enumerate(self.times):
            self.p['ML_interogation.duration'] = U(duration, 'us')
            self.program_pulser(sequence)
            [counts_bright, counts_dark] = self.run_sequence(max_runs=500, num=2)
            self.plot_prob(duration, counts_bright, counts_dark)
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break

    def setup_prob_datavault(self):
        self.dv.cd(['', 'ML_decoherence'], True, context=self.prob_ctx)

        self.dataset_prob = self.dv.new('ML_decoherence', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')],
                                        context=self.prob_ctx)
        self.grapher.plot(self.dataset_prob, 'ML_decoherence', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.prob_ctx)

    def plot_prob(self, delay, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(delay, prob_dark, prob_bright,
                    prob_bright - prob_dark, context=self.prob_ctx)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ML_decoherence(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
