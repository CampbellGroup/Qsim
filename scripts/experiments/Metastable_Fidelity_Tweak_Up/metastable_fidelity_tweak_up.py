import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.pulse_sequences.metastable_three_preparation import metastable_three_preparation as metastable_bright_sequence  # this is where I define which state is bright
from Qsim.scripts.pulse_sequences.metastable_four_preparation import metastable_four_preparation as metastable_dark_sequence

import numpy as np
from labrad.units import WithUnit as U


class metastable_fidelity_tweak_up(QsimExperiment):
    """
   
    """

    name = 'Metastable Fidelity Tweak Up'
    
    exp_parameters = []

    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))

    exp_parameters.extend(metastable_bright_sequence.all_required_parameters())
    exp_parameters.extend(metastable_dark_sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context

    def run(self, cxn, context):

        self.p['Line_Selection.qubit'] = 'qubit_0'
        self.p['MicrowaveInterrogation.duration'] = self.p.Pi_times.qubit_0
        self.p['MicrowaveInterrogation.detuning'] = U(0.0, 'kHz')

        self.p['Metastable_Microwave_Interrogation.duration'] = self.p.Pi_times.metastable_qubit
        self.p['Metastable_Microwave_Interrogation.detuning'] = U(0.0, 'kHz')

        self.p['Modes.state_detection_mode'] = 'Shelving'

        self.setup_prob_datavault()

        i = 0
        while True:
            i += 1

            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            # programs and runs the bright state sequence, then creates an array with exp number, detection
            # counts, and doppler counts to be saved to datavault
            self.program_pulser(metastable_bright_sequence)
            [counts_doppler_bright, counts_herald_bright_1, counts_herald_bright_2,  counts_bright] = self.run_sequence(max_runs=250, num=4)
            failed_four_heralding_bright = np.where(counts_herald_bright_1 >= self.p.ShelvingStateDetection.state_readout_threshold)
            failed_three_heralding_bright = np.where(counts_herald_bright_2 >= self.p.ShelvingStateDetection.state_readout_threshold)
            doppler_errors_bright = np.where(counts_doppler_bright <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            all_bright_errors = np.unique(np.concatenate((failed_three_heralding_bright[0], failed_four_heralding_bright[0], doppler_errors_bright[0])))
            counts_bright_fixed = np.delete(counts_bright, all_bright_errors)


            self.program_pulser(metastable_dark_sequence)
            [counts_doppler_dark, counts_herald_dark, counts_dark] = self.run_sequence(max_runs=333, num=3)
            failed_heralding_dark = np.where(counts_herald_dark >= self.p.ShelvingStateDetection.state_readout_threshold)
            doppler_errors_dark = np.where(counts_doppler_dark <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            all_dark_errors = np.unique(np.concatenate((failed_heralding_dark[0], doppler_errors_dark[0])))
            counts_dark_fixed = np.delete(counts_dark, all_dark_errors)
           

            # this processes the counts and calculates the fidelity and plots it on the bottom panel
            self.plot_prob(i, counts_dark_fixed, counts_bright_fixed)

            # process the count_bins and return the histogram with bins and photon counts/bin
            hist_bright = self.process_data(counts_bright_fixed)
            hist_dark = self.process_data(counts_dark_fixed)

            # this part plots the histograms on the hist panel in the shelving_fidelity tab
            self.plot_hist(hist_bright, folder_name='Metastable_Bright_Histogram')
            self.plot_hist(hist_dark, folder_name='Metastable_Dark_Histogram')



    def plot_prob(self, num, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright,
            prob_bright - prob_dark, context=self.prob_context)

    def setup_prob_datavault(self):
        self.prob_context = self.dv.context()
        self.dv.cd(['', 'Metastable_Fidelity'], True, context=self.prob_context)

        self.dataset_prob = self.dv.new('metastable_fidelity', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')], context=self.prob_context)
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.prob_context)

    def finalize(self, cxn, context):
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = metastable_fidelity_tweak_up(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
