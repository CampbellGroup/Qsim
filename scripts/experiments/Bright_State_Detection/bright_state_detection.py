import labrad
from Qsim.scripts.pulse_sequences.bright_state_preperation import bright_state_preperation as sequence
from Qsim.scripts.pulse_sequences.dark_state_preperation import dark_state_preperation as shelving_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np


class BrightStateDetection(QsimExperiment):
    """
    Perform preparation of the bright state for either shelving or standard detection,
    and plot histograms and readout fidelity of the bright state continuously
    """

    name = 'Bright State Detection'

    exp_parameters = []
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = self.cxn.pulser
        self.rsg = self.cxn.grapher
        self.prob_ctx = self.dv.context()
        self.hist_ctx = self.dv.context()

    def run(self, cxn, context):
        mode = self.p.Modes.state_detection_mode
        self.setup_prob_datavault()
        i = 0

        # program the correct sequence depending on detection method
        if mode == 'Standard':
            self.program_pulser(sequence)
        elif mode == 'Shelving':
            self.program_pulser(shelving_sequence)

        # run loop continuously until user stops experiment
        while True:
            i += 1
            points_per_hist = self.p.StandardStateDetection.points_per_histogram

            # run and process data if detection mode is shelving
            if mode == 'Shelving':
                [doppler_counts, counts] = self.run_sequence(max_runs=500, num=2)
                doppler_errors = np.where(doppler_counts <= self.p.DopplerCooling.doppler_counts_threshold)
                counts = np.delete(counts, doppler_errors)
                print doppler_errors

            # run and process data if detection mode is standard
            elif mode == 'Standard':
                [counts] = self.run_sequence(max_runs=1000)

            # process counts into a histogram and plot on grapher
            if i % points_per_hist == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist, folder_name='Bright_State_Detection')

            self.plot_prob(i, counts)

            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                if mode == 'Standard':
                    self.program_pulser(sequence)
                elif mode == 'Shelving':
                    self.program_pulser(shelving_sequence)

    def setup_prob_datavault(self):
        self.dv.cd(['', 'Bright_State_Probability'],
                   True, context=self.prob_ctx)
        self.dataset_prob = self.dv.new('fidelity_bright_state_prep',
                                        [('run', 'arb u')],
                                        [('Counts', 'Counts', 'num')],
                                        context=self.prob_ctx)

        self.rsg.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.prob_ctx)

    def plot_prob(self, num, counts):
        prob = self.get_pop(counts)
        self.dv.add(num, prob, context=self.prob_ctx)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = BrightStateDetection(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
