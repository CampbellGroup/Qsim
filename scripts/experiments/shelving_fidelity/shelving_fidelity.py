import labrad
from Qsim.scripts.pulse_sequences.shelving_fidelity import shelving_fidelity as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.Rabi_Point_Tracker.rabi_point_tracker import RabiPointTracker
#from Qsim.scripts.experiments.interleaved_linescan.interleaved_linescan import InterleavedLinescan
#from Qsim.scripts.experiments.shelving_411.shelving_411 import ShelvingRate
#from Qsim.scripts.experiments.Microwave_Ramsey_Experiment.microwave_ramsey_experiment import MicrowaveRamseyExperiment
#from Qsim.scripts.pulse_sequences.bright_state_prepepration import bright_state_preperation
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
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'sequence_iterations'))

    exp_parameters.append(('Timetags', 'save_timetags'))
    exp_parameters.append(('Timetags', 'lower_threshold'))
    exp_parameters.append(('Timetags', 'upper_threshold'))
    exp_parameters.append(('MicrowaveInterogation', 'AC_line_trigger'))
    exp_parameters.append(('MicrowaveInterogation', 'delay_from_line_trigger'))
    exp_parameters.append(('RabiPointTracker', 'shelving_fidelity_drift_tracking'))
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('MicrowaveInterogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        if self.p.MicrowaveInterogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterogation.delay_from_line_trigger)

        qubit = self.p.Line_Selection.qubit
        collect_timetags = self.p.Timetags.save_timetags
        if qubit == 'qubit_0':
            self.pi_time = self.p.Pi_times.qubit_0

        elif qubit == 'qubit_plus':
            self.pi_time = self.p.Pi_times.qubit_plus

        elif qubit == 'qubit_minus':
            self.pi_time = self.p.Pi_times.qubit_minus

        self.p['MicrowaveInterogation.duration'] = self.pi_time
        self.p['MicrowaveInterogation.detuning'] = U(0.0, 'kHz')
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.setup_prob_datavault()
        self.setup_timetags_datavault()
        self.program_pulser(sequence)

        i = 0
        while i < self.p.ShelvingStateDetection.sequence_iterations:
            i += 1
            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()

            self.p = self.parameters
            if self.p != old_params:
                self.program_pulser(sequence)

            if collect_timetags == 'OFF':
                [counts_doppler_bright, counts_bright, counts_doppler_dark, counts_dark] = self.run_sequence(max_runs=250, num=4)
            elif collect_timetags == 'ON':
                [counts_doppler_bright, counts_bright, counts_doppler_dark, counts_dark], timetags = self.run_sequence_with_timetags(max_runs=150, num=4)
                timetags_bright, timetags_dark = self.process_timetags(timetags, counts_bright, counts_dark)
                self.save_suspicious_detection_events(counts_bright, counts_dark, timetags_bright, timetags_dark)

            # delete the experiments where the ion wasnt properly doppler cooled
            counts_bright, counts_dark, n_errors = self.delete_doppler_count_errors(counts_doppler_bright, counts_doppler_dark,
                                                                                    counts_bright, counts_dark)
            print('Total doppler errors = ' + str(n_errors))
            print('Total bright events = ' + str(len(counts_bright)))
            print('Total dark events = ' + str(len(counts_dark)))
            print 'Mean Doppler Counts:', (np.mean(counts_doppler_bright) + np.mean(counts_doppler_dark))/2.0

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

        # reset the line trigger and delay to false
        self.pulser.line_trigger_state(False)

    def setup_prob_datavault(self):
        self.dv_context = self.dv.context()
        self.dv.cd(['', 'shelving_fidelity'], True, context=self.dv_context)

        self.dataset_prob = self.dv.new('shelving_fidelity', [('run', 'prob')],
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

    def process_timetags(self, timetags, counts_bright, counts_dark):
        # function should take in the timetags, and parse into a list of lists for the timetags
        # during each  state detection sequence
        ttBright = []
        ttDark = []
        tt = timetags[0]
        for b, d in zip(counts_bright, counts_dark):
            tempBright = tt[:int(b)]
            tempDark = tt[int(b):int(d + b)]
            ttBright.append(tempBright)
            ttDark.append(tempDark)
            tt = tt[int(b + d):]
        return ttBright, ttDark

    def delete_doppler_count_errors(self, counts_doppler_bright, counts_doppler_dark, counts_bright, counts_dark):
        """
        takes in the photon counts from each experiment, and the doppler cooling counts for each experiment. Deletes
        the fidelity measurements where the doppler cooling counts were below a user specified threshold, and pads the
        error mitigation by deleting the experiment before and after the identified experiment
        """

        padWidth = 1
        bright_errors = np.where(counts_doppler_bright <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
        bright_delete = np.array([])
        for error in bright_errors[0]:
            # we are going to delete the experiments 1 before and after the error for safety
            tempPad = range(error - padWidth, error + padWidth + 1, 1)
            bright_delete = np.concatenate((bright_delete, tempPad))
        bright_delete = bright_delete[(bright_delete < len(counts_doppler_bright)) & (bright_delete >= 0.0)]
        counts_bright_fixed = np.delete(counts_bright, bright_delete)

        dark_errors = np.where(counts_doppler_dark <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
        dark_delete = np.array([])
        for error in dark_errors[0]:
            # we are going to delete the experiments 1 before and after the error for safety
            tempPad = range(error - padWidth, error + padWidth + 1, 1)
            dark_delete = np.concatenate((dark_delete, tempPad))
        dark_delete = dark_delete[(dark_delete < len(counts_doppler_dark)) & (dark_delete >= 0.0)]
        counts_dark_fixed = np.delete(counts_dark, dark_delete)

        total_doppler_errors = len(bright_errors[0]) + len(dark_errors[0])
        return counts_bright_fixed, counts_dark_fixed, total_doppler_errors

    def save_suspicious_detection_events(self, counts_bright, counts_dark, timetags_bright, timetags_dark):
        """
        This saves the timetags to a file for detection events where the number of counted photons falls
        within a user specified range. The first column of the data saved will contain the number of
        counted photons for the first corresponding timetag entry, and the second column will be the
        timetags themselves. So it may look something like [(2, detectionevent1tt),(0,detectionevent1tt),
        (1, detectionevent2tt), (2, detectionevent3tt), (0, detectionevent3tt)]
        """
        save_bright_timetags = np.where(counts_bright <= self.p.Timetags.upper_threshold)
        save_dark_timetags = np.where(counts_dark >= self.p.Timetags.lower_threshold)

        for locationBright, locationDark in zip(save_bright_timetags[0], save_dark_timetags[0]):
            countsBright = int(counts_bright[int(locationBright)])
            countsDark = int(counts_dark[int(locationDark)])
            # if a non-zero number of photons were timetagged, save them to datavault
            if countsBright != 0:
                col1 = np.zeros(countsBright)
                col1[0] = countsBright
                self.dv.add(np.column_stack((col1,
                                             np.array(timetags_bright[int(locationBright)]))),
                            context=self.tt_bright_context)

            if countsDark != 0:
                col1 = np.zeros(countsDark)
                col1[0] = countsDark
                self.dv.add(np.column_stack((col1,
                                             np.array(timetags_dark[int(locationDark)]))), context=self.tt_dark_context)

    def run_rabi_tracking(self):
        """
        This should run the rabi tracking subroutine that performs a preparation of the
        dark state, and does 100T_Pi and detects the population left in the bright state.
        These values are then logged and decisions can be made later on what to do with it
        """
        rabi_track_context = self.sc.context()

        # collect the initial settings of some parameters from the base experiment (shelving_fidelity)
        init_microwave_sequence = self.p.MicrowaveInterogation.pulse_sequence
        init_optical_pumping_mode = self.p.OpticalPumping.method

        # manually force all the parameters how you want them for the drift tracking experiment, which
        # can in practice be very different from what we use in the high fidelity measurement
        self.p['MicrowaveInterogation.pulse_sequence'] = 'standard'
        self.p['OpticalPumping.method'] = 'Standard'
        self.p['Modes.state_detection_mode'] = 'Standard'
        self.p['MicrowaveInterogation.duration'] = 100.0 * self.pi_time

        # make the experiment, initialize it, and run it.
        self.rabi_tracker = self.make_experiment(RabiPointTracker)
        self.rabi_tracker.initialize(self.cxn, rabi_track_context, self.ident)
        pop = self.rabi_tracker.run(self.cxn, rabi_track_context)

        # return the parameters to their intial states, including some additional ones that
        # may be changed in the rabi tracking run() method
        self.p['MicrowaveInterogation.pulse_sequence'] = init_microwave_sequence
        self.p['OpticalPumping.method'] = init_optical_pumping_mode
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.p['MicrowaveInterogation.duration'] = self.pi_time
        self.p['MicrowaveInterogation.detuning'] = U(0.0, 'kHz')

        # reprogram the pulser with the sequence defined in this experiment (shelving_fidelity)
        self.program_pulser(sequence)

        return pop

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = shelving_fidelity(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
