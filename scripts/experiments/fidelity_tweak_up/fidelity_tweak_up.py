import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.bright_state_preperation import bright_state_preperation as sequence_bright
from Qsim.scripts.pulse_sequences.dark_state_preperation import dark_state_preperation as sequence_dark
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment


class fidelity_tweak_up(QsimExperiment):
    """
    Doppler cool ion the readout bright fidelity
    """

    name = 'Fidelity Tweak Up'

    exp_parameters = []
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.extend(sequence_bright.all_required_parameters())
    exp_parameters.extend(sequence_dark.all_required_parameters())


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pmt = self.cxn.normalpmtflow
        self.init_mode = self.pmt.getcurrentmode()
        self.pmt.set_mode('Normal')
        self.pulser = self.cxn.pulser
        self.rsg = self.cxn.grapher
        self.prob_ctx = self.dv.context()
        self.hist_ctx = self.dv.context()

    def run(self, cxn, context):

        self.setup_prob_datavault()
        i = 0
        while True:
            i+=1
            counts_dark = self.program_pulser(sequence_dark)
            counts_bright = self.program_pulser(sequence_bright)
            hist_dark = self.process_data(counts_dark)
            hist_bright = self.process_data(counts_bright)
            if i % 10 == 0:
                self.setup_hist_datavault('Dark')
                self.plot_hist(hist_dark)
                self.setup_hist_datavault('Bright')
                self.plot_hist(hist_bright)
            self.plot_prob(i, counts_bright, counts_dark)
            should_break = self.update_progress(np.random.random())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters

    def program_pulser(self, sequence):

        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(int(self.p.StateDetection.repititions))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        counts = self.pulser.get_readout_counts()
        self.pulser.reset_readout_counts()
        return counts

    def setup_hist_datavault(self, state):
        self.dv.cd(['', state + '_State_Detection'], True, context=self.hist_ctx)
        self.dataset_hist = self.dv.new(state + '_state_prep', [('run', 'arb u')],
                                        [('Counts', 'Counts', 'num')], context = self.hist_ctx)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hist_ctx)


    def setup_prob_datavault(self):
        self.dv.cd(['', 'fidelity_tweak_up'], True, context=self.prob_ctx)

        self.dataset_prob = self.dv.new('fidelity_tweak_up', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')], context=self.prob_ctx)
        self.rsg.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context = self.prob_ctx)

    def process_data(self, counts):
        data = np.column_stack((np.arange(self.p.StateDetection.repititions), counts))
        y = np.histogram(data[:, 1], int(np.max([data[:, 1].max() - data[:, 1].min(), 1])))
        counts = y[0]
        bins = y[1][:-1]
        if bins[0] < 0:
            bins = bins + .5
        hist = np.column_stack((bins, counts))
        return hist

    def plot_hist(self, hist):
        self.dv.add(hist, context=self.hist_ctx)
        self.rsg.plot(self.dataset_hist, 'Histogram', False)

    def plot_prob(self, num, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright, prob_bright - prob_dark, context = self.prob_ctx)

    def get_pop(self, counts):
        self.thresholdVal = self.p.StateDetection.state_readout_threshold
        prob = len(np.where(counts > self.thresholdVal)[0])/float(len(counts))
        return prob

    def finalize(self, cxn, context):
        self.pmt.set_mode(self.init_mode)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = fidelity_tweak_up(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
