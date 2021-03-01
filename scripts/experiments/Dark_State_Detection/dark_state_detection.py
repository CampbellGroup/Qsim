import labrad
from labrad.units import WithUnit as U
from Qsim.scripts.pulse_sequences.dark_state_preparation import dark_state_preparation as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.Interleaved_Linescan.interleaved_linescan import interleaved_linescan
from scipy.optimize import curve_fit as fit

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
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('MicrowaveInterrogation', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('RabiPointTracker', 'shelving_fidelity_drift_tracking'))
    exp_parameters.append(('BrightStatePumping', 'microwave_phase_list'))
    exp_parameters.extend(sequence.all_required_parameters())

    # manually set these parameters in the experiment
    exp_parameters.remove(('MicrowaveInterrogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterrogation', 'duration'))


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = self.cxn.pulser
        self.rsg = self.cxn.grapher
        self.pzt_server = cxn.piezo_server
        self.prob_ctx = self.dv.context()
        self.hist_ctx = self.dv.context()
        self.mean_doppler_counts = 0.0
        self.cavity_chan = 1
        self.cavity_voltage = 0.0
        self.hist_mean = 0.0
        self.hist_std_dev = 0.0

    def run(self, cxn, context):

        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
        self.init_line_center = self.run_interleaved_linescan()
        print('Initial line center at ' + str(self.init_line_center))

        # fix the interrogation time to be the pi_time and the detuning to be 0
        self.p['MicrowaveInterrogation.duration'] = self.p.Pi_times.qubit_0
        self.p['MicrowaveInterrogation.detuning'] = U(0.0, 'kHz')

        mode = self.p.Modes.state_detection_mode
        self.setup_prob_datavault()
        i = 0

        # run loop continuously until user stops experiment
        while True:
            i += 1
            points_per_hist = self.p.StandardStateDetection.points_per_histogram
            self.program_pulser(sequence)
            # run and process data if detection mode is shelving
            if mode == 'Shelving':
                [doppler_counts, counts] = self.run_sequence(max_runs=500, num=2)
                dark_dataset = np.column_stack((np.arange(len(counts)), np.array(counts), np.array(doppler_counts)))
                self.dv.add(dark_dataset, context=self.dark_state_counts)
                counts, total_doppler_errors = self.delete_doppler_count_errors(doppler_counts, counts)

                print 'Deleted' + str(total_doppler_errors) + ' experiments due to Doppler errors'

            # run and process data if detection mode is standard
            elif mode == 'Standard':
                [counts] = self.run_sequence(max_runs=1000)

            # process counts into a histogram and plot on grapher
            if i % points_per_hist == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist, folder_name='Dark_State_Detection')

            self.plot_prob(i, counts)
            if mode == 'Shelving':
                if i == 1:
                    self.hist_mean = np.mean(doppler_counts)
                    self.hist_std_dev = np.sqrt(np.mean(doppler_counts))
                    print('mean doppler counts on first experiment is  = ' + str(self.hist_mean))
                elif i > 1:
                    if (np.mean(doppler_counts) < (self.hist_mean - 1.0*self.hist_std_dev)) or (
                            np.mean(doppler_counts) > (self.hist_mean + 1.0*self.hist_std_dev)):
                        success = self.correct_cavity_drift()
                        if success:
                            self.hist_mean = np.mean(doppler_counts)
                            self.hist_std_dev = np.std(doppler_counts)
                        else:
                            break

            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                self.program_pulser(sequence)


            # if the phase list is random we want to always reprogram the pulser so that
            # a new set of random phases is set for the next set of N experiments
            if self.p.BrightStatePumping.microwave_phase_list == 'random':
                self.program_pulser(sequence)

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

        self.dark_state_counts = self.dv.context()
        self.dv.cd(['', 'Dark_State_Counts'], True, context=self.dark_state_counts)
        self.dark_state_counts_dataset = self.dv.new('dark_state_counts', [('run', 'arb')],
                                                     [('counts', 'detection_counts', 'num'),
                                                      ('counts', 'doppler_counts', 'num')],
                                                     context=self.dark_state_counts)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.dark_state_counts)

    def plot_prob(self, num, counts):
        prob = self.get_pop(counts)
        self.dv.add(num, prob, context=self.prob_ctx)

    def delete_doppler_count_errors(self, counts_doppler_dark,  counts_dark):
        """
        takes in the photon counts from each experiment, and the doppler cooling counts for each experiment. Deletes
        the fidelity measurements where the doppler cooling counts were below a user specified threshold, and pads the
        error mitigation by deleting the experiment before and after the identified experiment
        """

        padWidth = 1  # delete this many experiments before and after the detected doppler error
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

    def run_interleaved_linescan(self):
        self.pulser.line_trigger_state(False)

        linescan_context = self.sc.context()

        self.line_tracker = self.make_experiment(interleaved_linescan)
        self.line_tracker.initialize(self.cxn, linescan_context, self.ident)
        try:
            detunings, counts = self.line_tracker.run(self.cxn, linescan_context)
        except TypeError:
            return TypeError

        if max(counts) < 100:
            print("Lorentzian is weak or missing")
            return RuntimeError

        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        fit_guess = [5.0, 30.0, 4000.0, 1.0]
        try:
            popt, pcov = fit(self.lorentzian_fit, detunings[2:], counts[2:], p0=fit_guess)
        except RuntimeError:
            print('Fit did not work, returning RuntimeError from scipy.curve_fit')
            return RuntimeError

        center = popt[0]
        return center

    def lorentzian_fit(self, detuning, center, fwhm, scale, offset):
        return offset + scale * 0.5 * fwhm / ((detuning - center) ** 2 + (0.5 * fwhm) ** 2)

    def correct_cavity_drift(self):
        center_before = self.run_interleaved_linescan()
        if (center_before == RuntimeError) or (center_before == TypeError):
            return False

        delta = (self.init_line_center - center_before)  # cavity shift in MHz, no labrad units
        while np.abs(delta) > 1.0:

            new_cavity_voltage = self.cavity_voltage + (delta * 0.01)  # 0.01 V/ MHz on cavity
            if np.abs(new_cavity_voltage - self.cavity_voltage) < 0.5:
                self.pzt_server.set_voltage(self.cavity_chan, U(new_cavity_voltage, 'V'))
                self.cavity_voltage = new_cavity_voltage
            else:
                print('Linescan fit did not work, killing tweak up')
                break

            center_after = self.run_interleaved_linescan()
            if (center_after == RuntimeError) or (center_after == TypeError):
                return False

            delta = (self.init_line_center - center_after)

        print('Finished cavity tweak up, resuming experiment')
        return True

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DarkStateDetection(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
