import labrad
from Qsim.scripts.pulse_sequences.shelving_bright_spam import shelving_bright_spam as bright_sequence
from Qsim.scripts.pulse_sequences.shelving_dark_spam import shelving_dark_spam as dark_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np
from labrad.units import WithUnit as U


class high_fidelity_measurement(QsimExperiment):
    """
    This experiment is similar to the Shelving Fidelity measurement, but with a different organization
    of the pulse sequence and data analysis
    """

    name = 'High Fidelity Measurement'

    exp_parameters = []

    exp_parameters.append(('HighFidelityMeasurement', 'sequence_iterations'))

    exp_parameters.extend(bright_sequence.all_required_parameters())
    exp_parameters.extend(dark_sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context

        # initialize contexts for different datavault connections
        self.prob_context = self.dv.context()  # exp num vs prob
        self.tt_bright_context = self.dv.context()  # timetags from bright experiments
        self.tt_dark_context = self.dv.context()  # timetags from dark experiments
        self.hf_bright_context = self.dv.context()  # detection and doppler counts for bright
        self.hf_dark_context = self.dv.context()  # detection and doppler counts for dark





    def run(self, cxn, context):

        # set the line trigger state to the appropriate state
        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        self.p['Line_Selection.qubit'] = 'qubit_0'
        self.pi_time = self.p.Pi_times.qubit_0
        self.p['MicrowaveInterrogation.duration'] = self.pi_time
        self.p['MicrowaveInterrogation.detuning'] = U(0.0, 'kHz')
        self.p['Modes.state_detection_mode'] = 'Shelving'

        self.reps = self.p.ShelvingStateDetection.repetitions

        self.setup_high_fidelity_datavault()


        i = 0
        while i < self.p.HighFidelityMeasurement.sequence_iterations:
            i += 1

            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            # programs and runs the bright state sequence, then creates an array with exp number, detection
            # counts, and doppler counts to be saved to datavault
            self.program_pulser(bright_sequence)
            [counts_doppler_bright, counts_bright], ttBright = self.run_sequence_with_timetags(max_runs=500, num=2)
            bright_data = np.column_stack((np.arange(self.reps), counts_bright, counts_doppler_bright))

            # programs and runs the dark state sequence, then creates an array with exp number, detection
            # counts, and doppler counts to be saved to datavault
            self.program_pulser(dark_sequence)
            [counts_doppler_dark, counts_dark], ttDark = self.run_sequence_with_timetags(max_runs=500, num=2)
            dark_data = np.column_stack((np.arange(self.reps), counts_dark, counts_doppler_dark))

            # delete the experiments where the ion wasnt properly doppler cooled. created new arrays for
            # counts bright and counts dark so that original data is not modified from counts_bright,
            # counts_dark
            countsBright, countsDark, n_errors = self.delete_doppler_count_errors(counts_doppler_bright, counts_doppler_dark,
                                                                                    counts_bright, counts_dark)

            # this processes the counts and calculates the fidelity and plots it on the bottom panel
            self.plot_prob(i, countsBright, countsDark)

            # process the count_bins and return the histogram with bins and photon counts/bin
            hist_bright = self.process_data(countsBright)
            hist_dark = self.process_data(countsDark)

            # this part plots the histograms on the hist panel in the shelving_fidelity tab
            self.plot_hist(hist_bright, folder_name='Shelving_Histogram')
            self.plot_hist(hist_dark, folder_name='Shelving_Histogram')

    def setup_high_fidelity_datavault(self):

        # datavault setup for the run number vs probability plots
        self.dv.cd(['', 'high_fidelity_measurement'], True, context=self.prob_context)

        self.dataset_prob = self.dv.new('high_fidelity_measurement', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')], context=self.prob_context)
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.prob_context)


        # datavault setup for the timetags for bright and dark states in separate folders
        self.dv.cd(['', 'high_fidelity_timetags_bright'], True, context=self.tt_bright_context)
        self.tt_bright_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                             [('time', 'timetags', 'num')], context=self.tt_bright_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_bright_context)

        self.dv.cd(['', 'high_fidelity_timetags_dark'], True, context=self.tt_dark_context)
        self.tt_dark_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                           [('time', 'timetags', 'num')], context=self.tt_dark_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_dark_context)


        # datavault setup for the raw detection counts and doppler counts and experiment number for
        # every experiment performed, bright and dark separately
        self.dv.cd(['', 'high_fidelity_shelving_bright'], True, context=self.hf_bright_context)
        self.hf_bright_dataset = self.dv.new('high_fidelity_data', [('run', 'arb units')],
                                      [('counts', 'detection_counts'), ('counts', 'doppler_counts')],
                                      context=self.hf_bright_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hf_bright_context)

        self.dv.cd(['', 'high_fidelity_shelving_dark'], True, context=self.hf_dark_context)
        self.hf_dark_dataset = self.dv.new('high_fidelity_data', [('run', 'arb units')],
                                      [('counts', 'detection_counts'), ('counts', 'doppler_counts')],
                                      context=self.hf_dark_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hf_dark_context)

    def plot_prob(self, num, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright,
                    prob_bright - prob_dark, context=self.dv_context)

    def delete_doppler_count_errors(self, counts_doppler_bright, counts_doppler_dark, counts_bright, counts_dark):
        """
        takes in the photon counts from each experiment, and the doppler cooling counts for each experiment. Deletes
        the fidelity measurements where the doppler cooling counts were below a user specified threshold, and pads the
        error mitigation by deleting the experiments after the identified experiment
        """

        padding = 2
        bright_errors = np.where(counts_doppler_bright <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
        bright_delete = np.array([])
        for error in bright_errors[0]:
            # we are going to delete the experiments 1 before and after the error for safety
            tempPad = range(error, error + padding + 1, 1)
            bright_delete = np.concatenate((bright_delete, tempPad))
        bright_delete = bright_delete[(bright_delete < len(counts_doppler_bright)) & (bright_delete >= 0.0)]
        counts_bright_fixed = np.delete(counts_bright, bright_delete)

        dark_errors = np.where(counts_doppler_dark <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
        dark_delete = np.array([])
        for error in dark_errors[0]:
            # we are going to delete the experiments 1 before and after the error for safety
            tempPad = range(error, error + padding + 1, 1)
            dark_delete = np.concatenate((dark_delete, tempPad))
        dark_delete = dark_delete[(dark_delete < len(counts_doppler_dark)) & (dark_delete >= 0.0)]
        counts_dark_fixed = np.delete(counts_dark, dark_delete)

        total_doppler_errors = len(bright_errors[0]) + len(dark_errors[0])
        return counts_bright_fixed, counts_dark_fixed, total_doppler_errors

    def finalize(self, cxn, context):
        # reset the line trigger and delay to false
        self.pulser.line_trigger_state(False)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = high_fidelity_measurement(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
