import labrad
from Qsim.scripts.pulse_sequences.shelving_bright_spam import shelving_bright_spam as bright_sequence
from Qsim.scripts.pulse_sequences.shelving_dark_spam import shelving_dark_spam as dark_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.Rabi_Point_Tracker.rabi_point_tracker import RabiPointTracker
import numpy as np
from labrad.units import WithUnit as U


class high_fidelity_measurement(QsimExperiment):
    """
    This experiment is similar to the Shelving Fidelity measurement, but with a different organization
    of the pulse sequence and data analysis
    """

    name = 'Shelving Fidelity'

    exp_parameters = []

    exp_parameters.append(('HighFidelityMeasurement', 'sequence_iterations'))
    exp_parameters.append(('RabiPointTracker', 'shelving_fidelity_drift_tracking'))
    exp_parameters.append(('RabiPointTracker', 'number_pi_times'))

    exp_parameters.extend(bright_sequence.all_required_parameters())
    exp_parameters.extend(dark_sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context

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

        self.setup_prob_datavault()

        i = 0
        while i < self.p.ShelvingStateDetection.sequence_iterations:
            i += 1
            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            self.program_pulser(bright_sequence)
            [counts_doppler_bright, counts_bright] = self.run_sequence(max_runs=500, num=2)

            self.program_pulser(dark_sequence)
            [counts_doppler_dark, counts_dark] = self.run_sequence(max_runs=500, num=2)

            # delete the experiments where the ion wasnt properly doppler cooled
            counts_bright, counts_dark, n_errors = self.delete_doppler_count_errors(counts_doppler_bright, counts_doppler_dark,
                                                                                    counts_bright, counts_dark)

            # this runs the rabi tracking subroutine if the user chooses to do so. We force the value it
            # returns to 0.0 if we are not tracking since we are saving the data to datavault either way
            if self.p.RabiPointTracker.shelving_fidelity_drift_tracking == 'ON':
                rabi_point_tracking_pop = self.run_rabi_tracking()
            elif self.p.RabiPointTracker.shelving_fidelity_drift_tracking == 'OFF':
                rabi_point_tracking_pop = 0.0

            # this processes the counts and calculates the fidelity and plots it on the bottom panel
            self.plot_prob(i, counts_bright, counts_dark, rabi_point_tracking_pop)

            # process the count_bins and return the histogram with bins and photon counts/bin
            hist_bright = self.process_data(counts_bright)
            hist_dark = self.process_data(counts_dark)

            # this part plots the histograms on the hist panel in the shelving_fidelity tab
            self.plot_hist(hist_bright, folder_name='Shelving_Histogram')
            self.plot_hist(hist_dark, folder_name='Shelving_Histogram')

    def setup_prob_datavault(self):
        self.dv_context = self.dv.context()
        self.dv.cd(['', 'high_fidelity_measurement'], True, context=self.dv_context)

        self.dataset_prob = self.dv.new('high_fidelity_measurement', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num'),
                                         ('Prob', 'rabi_point_tracking', 'num')], context=self.dv_context)
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.dv_context)

    def setup_timetags_datavault(self):
        self.tt_bright_context = self.dv.context()
        self.dv.cd(['', 'timetagged_bright_errors'], True, context=self.tt_bright_context)
        self.tt_bright_dataset = self.dv.new('timetagged_errors', [('arb', 'arb')],
                                            [('time', 'timetags', 'num')], context=self.tt_bright_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_bright_context)

        self.tt_dark_context = self.dv.context()
        self.dv.cd(['', 'timetagged_dark_errors'], True, context=self.tt_dark_context)
        self.tt_dark_dataset = self.dv.new('timetagged_errors', [('arb', 'arb')],
                                             [('time', 'timetags', 'num')], context=self.tt_dark_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_dark_context)

    def plot_prob(self, num, counts_dark, counts_bright, rabi_point_tracking_prob):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright,
                    prob_bright - prob_dark, rabi_point_tracking_prob,
                    context=self.dv_context)

    def delete_doppler_count_errors(self, counts_doppler_bright, counts_doppler_dark, counts_bright, counts_dark):
        """
        takes in the photon counts from each experiment, and the doppler cooling counts for each experiment. Deletes
        the fidelity measurements where the doppler cooling counts were below a user specified threshold, and pads the
        error mitigation by deleting the experiment before and after the identified experiment
        """

        padWidth = 1
        bright_errors = np.where(counts_doppler_bright <= self.p.DopplerCooling.doppler_counts_threshold)
        bright_delete = np.array([])
        for error in bright_errors[0]:
            # we are going to delete the experiments 1 before and after the error for safety
            tempPad = range(error - padWidth, error + padWidth + 1, 1)
            bright_delete = np.concatenate((bright_delete, tempPad))
        bright_delete = bright_delete[(bright_delete < len(counts_doppler_bright)) & (bright_delete >= 0.0)]
        counts_bright_fixed = np.delete(counts_bright, bright_delete)

        dark_errors = np.where(counts_doppler_dark <= self.p.DopplerCooling.doppler_counts_threshold)
        dark_delete = np.array([])
        for error in dark_errors[0]:
            # we are going to delete the experiments 1 before and after the error for safety
            tempPad = range(error - padWidth, error + padWidth + 1, 1)
            dark_delete = np.concatenate((dark_delete, tempPad))
        dark_delete = dark_delete[(dark_delete < len(counts_doppler_dark)) & (dark_delete >= 0.0)]
        counts_dark_fixed = np.delete(counts_dark, dark_delete)

        total_doppler_errors = len(bright_errors[0]) + len(dark_errors[0])
        return counts_bright_fixed, counts_dark_fixed, total_doppler_errors

    def run_rabi_tracking(self):
        """
        This should run the rabi tracking subroutine that performs a preparation of the
        dark state, and does 100T_Pi and detects the population left in the bright state.
        These values are then logged and decisions can be made later on what to do with it
        """
        rabi_track_context = self.sc.context()

        init_microwave_sequence = self.p.MicrowaveInterogation.pulse_sequence
        init_optical_pumping_mode = self.p.OpticalPumping.method

        # manually force all the parameters how you want them for the drift tracking experiment, which
        # can in practice be very different from what we use in the high fidelity measurement
        self.p['MicrowaveInterrogation.pulse_sequence'] = 'standard'
        self.p['OpticalPumping.method'] = 'Standard'
        self.p['Modes.state_detection_mode'] = 'Standard'
        self.n_pi_times = self.p.RabiPointTracker.number_pi_times
        self.p['MicrowaveInterrogation.duration'] = self.n_pi_times * self.pi_time

        # make the experiment, initialize it, and run it.
        self.rabi_tracker = self.make_experiment(RabiPointTracker)
        self.rabi_tracker.initialize(self.cxn, rabi_track_context, self.ident)
        pop = self.rabi_tracker.run(self.cxn, rabi_track_context)


        # return the parameters to their intial states, including some additional ones that
        # may be changed in the rabi tracking run() method
        self.p['MicrowaveInterrogation.pulse_sequence'] = init_microwave_sequence
        self.p['OpticalPumping.method'] = init_optical_pumping_mode
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.p['MicrowaveInterrogation.duration'] = self.pi_time
        self.p['MicrowaveInterrogation.detuning'] = U(0.0, 'kHz')

        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        # DO NOT REPROGRAM PULSER HERE, IF YOU REPROGRAM AND THE EXPERIMENT GETS STOPPED BEOFRE THE
        # SEQUENCE CAN RUN THE PULSER WILL FREEZE UP!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        return pop

    def finalize(self, cxn, context):
        # reset the line trigger and delay to false
        self.pulser.line_trigger_state(False)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = high_fidelity_measurement(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
