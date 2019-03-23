import labrad
from Qsim.scripts.pulse_sequences.dark_state_preperation import dark_state_preperation as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np


class DarkStateDetection(QsimExperiment):
    """
    Optical pump ion dark then readout dark fidelity
    """

    name = 'Dark State Detection'

    exp_parameters = []
    exp_parameters.append(('DarkStateDetection', 'RunContinuous'))
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = self.cxn.pulser
        self.rsg = self.cxn.grapher
        self.prob_ctx = self.dv.context()
        self.hist_ctx = self.dv.context()

    def run(self, cxn, context):

        self.setup_prob_datavault()
        if self.p.DarkStateDetection.RunContinuous is True:
            i = 0
            self.program_pulser(sequence)
            while True:
                i += 1
                counts = self.run_sequence()
                hist = self.process_data(counts)
                if i % self.p.StandardStateDetection.points_per_histogram == 0:
                    self.setup_hist_datavault()
                    self.plot_hist(hist)
                self.plot_prob(i, counts)
                should_break = self.update_progress(np.random.random())
                if should_break:
                    break
                old_params = dict(self.p.iteritems())
                self.reload_all_parameters()
                self.p = self.parameters
                if self.p != old_params:
                    self.program_pulser(sequence)
        else:
            counts = self.program_pulser()
            hist = self.process_data(counts)
            self.setup_hist_datavault()
            self.plot_hist(hist)
            self.plot_prob(0, hist)

    def setup_hist_datavault(self):
        self.dv.cd(['', 'Dark_State_Detection'],
                   True, context=self.hist_ctx)
        self.dataset_hist = self.dv.new('dark_state_prep', [('run', 'arb u')],
                                        [('Counts', 'Counts', 'num')],
                                        context=self.hist_ctx)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.hist_ctx)

    def setup_prob_datavault(self):
        self.dv.cd(['', 'Dark_State_Probability'], True, context=self.prob_ctx)
        self.dataset_prob = self.dv.new('fidelity_dark_state_prep',
                                        [('run', 'arb u')],
                                        [('Counts', 'Counts', 'num')],
                                        context=self.prob_ctx)

        self.rsg.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.prob_ctx)

    def plot_hist(self, hist):
        self.dv.add(hist, context=self.hist_ctx)
        self.rsg.plot(self.dataset_hist, 'Histogram', False)

    def plot_prob(self, num, counts):
        prob = self.get_pop(counts)
        self.dv.add(num, prob, context=self.prob_ctx)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DarkStateDetection(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
