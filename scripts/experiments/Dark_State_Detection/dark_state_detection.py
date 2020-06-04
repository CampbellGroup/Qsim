import labrad
from labrad.units import WithUnit as U
from Qsim.scripts.pulse_sequences.dark_state_preperation import dark_state_preperation as sequence
from Qsim.scripts.pulse_sequences.bright_state_preperation import bright_state_preperation as shelving_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.Rabi_Point_Tracker.rabi_point_tracker import RabiPointTracker

import numpy as np


class DarkStateDetection(QsimExperiment):
    """
    Prepare the ion in the dark state (changes depending on the detection method),
    and readout repeatedly in a continuous fashion until the use stops the experiment
    """

    name = 'Dark State Detection'

    exp_parameters = []
    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'repititions'))
    exp_parameters.append(('MicrowaveInterogation', 'repititions')) 
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('RabiPointTracker', 'shelving_fidelity_drift_tracking'))
    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.extend(shelving_sequence.all_required_parameters())

    # manually set these parameters in the experiment
    exp_parameters.remove(('MicrowaveInterogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterogation', 'duration'))


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = self.cxn.pulser
        self.rsg = self.cxn.grapher
        self.prob_ctx = self.dv.context()
        self.hist_ctx = self.dv.context()

    def run(self, cxn, context):

        # choose which qubit will be driven
        qubit = self.p.Line_Selection.qubit
        reps = self.p.MicrowaveInterogation.repititions
        if qubit == 'qubit_0':
            self.pi_time = self.p.Pi_times.qubit_0
        elif qubit == 'qubit_plus':
            self.pi_time = self.p.Pi_times.qubit_plus
        elif qubit == 'qubit_minus':
            self.pi_time = self.p.Pi_times.qubit_minus

        # fix the interrogation time to be the pi_time and the detuning to be 0
        self.p['MicrowaveInterogation.duration'] = reps*self.pi_time
        self.p['MicrowaveInterogation.detuning'] = U(0.0, 'kHz')

        self.mode = self.p.Modes.state_detection_mode
        self.setup_prob_datavault()
        i = 0

        # program the correct sequence depending on detection method
        if self.mode == 'Standard':
            self.program_pulser(sequence)
        elif self.mode == 'Shelving':
            self.program_pulser(shelving_sequence)

        # run loop continuously until user stops experiment
        while True:
            i += 1
            points_per_hist = self.p.StandardStateDetection.points_per_histogram

            # run and process data if detection mode is shelving
            if self.mode == 'Shelving':
                [doppler_counts, counts] = self.run_sequence(max_runs=500, num=2)
                counts, total_doppler_errors = self.delete_doppler_count_errors(doppler_counts, counts)

                print 'Deleted' + str(total_doppler_errors) + ' experiments due to Doppler errors'

            # run and process data if detection mode is standard
            elif self.mode == 'Standard':
                [counts] = self.run_sequence(max_runs=1000)

            # process counts into a histogram and plot on grapher
            if i % points_per_hist == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist, folder_name='Dark_State_Detection')

            if self.p.RabiPointTracker.shelving_fidelity_drift_tracking == 'ON':
                rabi_point_tracking_pop = self.run_rabi_tracking()
            elif self.p.RabiPointTracker.shelving_fidelity_drift_tracking == 'OFF':
                rabi_point_tracking_pop = 0.0

            self.plot_prob(i, counts, rabi_point_tracking_pop)

            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                self.program_pulser(sequence)

    def setup_prob_datavault(self):
        self.dv.cd(['', 'Dark_State_Probability'], True, context=self.prob_ctx)
        self.dataset_prob = self.dv.new('fidelity_dark_state_prep',
                                        [('run', 'arb u')],
                                        [('Counts', 'Counts', 'num'),
                                         ('Prob', 'Rabi point tracking', 'num')],
                                        context=self.prob_ctx)

        self.rsg.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.prob_ctx)

    def plot_prob(self, num, counts, rabi_point_tracking_prob):
        prob = self.get_pop(counts)
        self.dv.add(num, prob, rabi_point_tracking_prob, context=self.prob_ctx)

    def delete_doppler_count_errors(self, counts_doppler_dark,  counts_dark):
        """
        takes in the photon counts from each experiment, and the doppler cooling counts for each experiment. Deletes
        the fidelity measurements where the doppler cooling counts were below a user specified threshold, and pads the
        error mitigation by deleting the experiment before and after the identified experiment
        """

        padWidth = 1 # delete this many experiments before and after the detected doppler error
        dark_errors = np.where(counts_doppler_dark <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
        dark_delete = np.array([])
        for error in dark_errors[0]:
            # we are going to delete the experiments 1 before and after the error for safety
            tempPad = range(error - padWidth, error + padWidth + 1, 1)
            dark_delete = np.concatenate((dark_delete, tempPad))
        dark_delete = dark_delete[(dark_delete < len(counts_doppler_dark)) & (dark_delete >= 0.0)]
        counts_dark_fixed = np.delete(counts_dark, dark_delete)

        total_doppler_errors = len(dark_errors[0])
        return counts_dark_fixed, total_doppler_errors

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
        print(pop)
        # return the parameters to their intial states, including some additional ones that
        # may be changed in the rabi tracking run() method
        self.p['MicrowaveInterogation.pulse_sequence'] = init_microwave_sequence
        self.p['OpticalPumping.method'] = init_optical_pumping_mode
        self.p['Modes.state_detection_mode'] = self.mode
        self.p['MicrowaveInterogation.duration'] = self.pi_time
        self.p['MicrowaveInterogation.detuning'] = U(0.0, 'kHz')

        # reprogram the pulser with the sequence defined in this experiment (shelving_fidelity)
        if self.mode == 'Shelving':
            self.program_pulser(shelving_sequence)
        elif self.mode == 'Standard':
            self.program_pulser(sequence)

        return pop

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DarkStateDetection(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
