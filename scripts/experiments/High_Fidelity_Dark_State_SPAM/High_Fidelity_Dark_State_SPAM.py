import labrad
import numpy as np
from scipy.optimize import curve_fit as fit
from labrad.units import WithUnit as U
import time

from Qsim.scripts.pulse_sequences.shelving_dark_spam import shelving_dark_spam as dark_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.Interleaved_Linescan.interleaved_linescan import interleaved_linescan
from Qsim.scripts.experiments.Microwave_Linescan.microwave_linescan import MicrowaveLineScan



class high_fidelity_dark_state_spam(QsimExperiment):
    """
    This experiment is similar to the high_fidelity_measurement experiment, but attempts to
    make further improvements by adding more drift tracking experiments and potentially trap
    reloading attempts
    """

    name = 'High Fidelity Dark State SPAM'

    exp_parameters = [
        ('Shelving_Doppler_Cooling', 'threshold_std_dev'),
        ('HighFidelityMeasurement', 'sequence_iterations')
    ]


    exp_parameters.extend(dark_sequence.all_required_parameters())


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context
        self.pzt_server = cxn.piezo_server
        self.ttl_server = cxn.arduinottl

        self.state_detection_ttl_chan = 12
        self.protection_beam_ttl_chan = 9
        self.cavity_chan = 1
        self.cavity_voltage = 0.0
        self.counts_track_mean = 0.0
        self.counts_track_std_dev = 0.0
        self.init_line_center = 0.0  # self.p.Transitions.main_cooling_369['MHz']
        self.wm_cxn = labrad.connect('10.97.112.2', password='lab')
        self.mp_server = self.wm_cxn.multiplexerserver
        self.dac_port_822 = 3
        self.init_dac_port_822_voltage = 0.0

    def run(self, cxn, context):

        # set the line trigger state to the appropriate state
        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        self.ttl_server.ttl_output(self.state_detection_ttl_chan, True) #block the state detection beam
        self.ttl_server.ttl_output(self.protection_beam_ttl_chan, True) #block the state detection beam

        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
        self.init_line_center = self.run_interleaved_linescan()  # measure where the line is, needs to be before set_fixed_params
        self.init_dac_port_822_voltage = self.mp_server.get_output_voltage(self.dac_port_822)  # gets the init dac port voltage for the M2 lock
        self.set_fixed_params()  # force certain parameters to have fixed values
        self.setup_high_fidelity_datavault()  # setup datavault folders for receiving HiFi data
        self.reps = self.p.ShelvingStateDetection.repetitions

        print('Init DAC voltage is ' + str(self.init_dac_port_822_voltage) + ' mV')

        i = 0
        while i < self.p.HighFidelityMeasurement.sequence_iterations:

            i += 1

            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            detection_delay_dark = self.get_detection_timetags_offset()

            self.program_pulser(dark_sequence)

            [counts_doppler_dark, counts_dark], ttDark = self.run_sequence_with_timetags(max_runs=250, num=2)

            dac_voltage = self.mp_server.get_output_voltage(self.dac_port_822)
            if np.abs(dac_voltage - self.init_dac_port_822_voltage) > 200.0:
                print('M2 Etalon hopped on experiment ' + str(i) + ', killing experiment.')
                break

            if (sum(counts_doppler_dark) + sum(counts_dark)) > 30000.0:
                print('Too many timetags, reduce number of experiments')
                break

            ttDark = ttDark[0]
            ttD_dop, ttD_det = self.parse_timetags(ttDark, counts_doppler_dark, counts_dark)
            ttD_det = np.array(ttD_det) - detection_delay_dark
            self.save_dark_data([counts_dark, counts_doppler_dark], [ttD_det, ttD_dop])

            countsDark, n_errors = self.delete_doppler_count_errors(counts_doppler_dark, counts_dark)

            # this checks to make sure we didn't lose the ion, effectively, and breaks the loop before a zero division
            # error occurs in plot_prob so that data gets saved
            if len(countsDark) == 0:
                print('Ion may have died, zero counts')
                break

            self.plot_prob(i, countsDark)
            self.process_histogram(countsDark)

            # this part of the loop checks the doppler counts to make sure cavity isnt drifting
            if i == 1:
                self.counts_track_mean = np.mean(counts_doppler_dark)
                self.counts_track_std_dev = np.sqrt(self.counts_track_mean)
                print('mean doppler counts on first experiment is  = ' + str(self.counts_track_mean))
            elif i > 1:
                last_exp_mean = np.mean(counts_doppler_dark)
                print('Mean doppler counts on last experiment was = ' + str(last_exp_mean) + ' counts')
                if (last_exp_mean < (self.counts_track_mean - self.counts_track_std_dev)) or (last_exp_mean > (self.counts_track_mean + self.counts_track_std_dev)):
                    success, iterations = self.correct_cavity_drift()
                    if success == True & iterations == 1:
                        self.counts_track_mean = last_exp_mean
                        self.counts_track_std_dev = np.sqrt(last_exp_mean)
                    elif success == True & iterations != 1:
                        pass
                    elif success == False:
                        break


    def process_histogram(self, countsDark):
        # process the count_bins and return the histogram with bins and photon counts/bin
        hist_dark = self.process_data(countsDark)

        # this part plots the histograms on the hist panel in the shelving_fidelity tab
        self.plot_hist(hist_dark, folder_name='Shelving_Histogram')

    def set_fixed_params(self):
        self.p['Line_Selection.qubit'] = 'qubit_0'
        self.pi_time = self.p.Pi_times.qubit_0
        self.p['MicrowaveInterrogation.duration'] = self.pi_time
        self.p['MicrowaveInterrogation.detuning'] = U(0.0, 'kHz')
        self.p['MicrowaveInterrogation.microwave_phase'] = U(0.0, 'deg')
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.p['Deshelving.power1'] = self.p.ddsDefaults.repump_760_1_power
        self.p['Deshelving.power2'] = self.p.ddsDefaults.repump_760_2_power
        self.p['Deshelving.repump_power'] = self.p.ddsDefaults.repump_935_power
        self.p['HighFidelityMeasurement.drift_tracking'] = 'On'
        self.p['Transitions.main_cooling_369'] = U(self.init_line_center, 'MHz')
        print('Initial 369 line center at ' + str(self.init_line_center)[:8] + ' MHz')

    def plot_prob(self, num, counts_dark):
        prob_dark = self.get_pop(counts_dark)
        self.dv.add(num, prob_dark, context=self.prob_context)

    def save_dark_data(self, counts, timetags):
        [counts_dark, counts_doppler_dark] = counts
        [timetags_det_dark, timetags_dop_dark] = timetags

        dark_data = np.column_stack((np.arange(len(counts_dark)), np.array(counts_dark), np.array(counts_doppler_dark)))
        self.dv.add(dark_data, context=self.hf_dark_context)
        self.dv.add(np.column_stack((np.zeros(len(timetags_det_dark)), np.array(timetags_det_dark))),
                    context=self.tt_dark_det_context)
        self.dv.add(np.column_stack((np.zeros(len(timetags_dop_dark)), np.array(timetags_dop_dark))),
                    context=self.tt_dark_dop_context)

    def delete_doppler_count_errors(self, counts_doppler_dark, counts_dark):
        """
        takes in the photon counts from each experiment, and the doppler cooling counts for each experiment. Deletes
        the fidelity measurements where the doppler cooling counts were below a user specified threshold
        """
        doppler_mean = np.mean(np.where(counts_doppler_dark > 20.0)[0])
        doppler_std_dev = np.sqrt(doppler_mean)
        dark_errors = np.where(counts_doppler_dark <= doppler_mean -
                               self.p.Shelving_Doppler_Cooling.threshold_std_dev * doppler_std_dev)
        counts_dark_fixed = np.delete(counts_dark, dark_errors)

        total_doppler_errors = len(dark_errors[0])
        return counts_dark_fixed, total_doppler_errors

    def setup_high_fidelity_datavault(self):
        # datavault setup for the run number vs probability plots
        self.prob_context = self.dv.context()
        self.dv.cd(['', 'shelving_probability_vs_runs'], True, context=self.prob_context)

        self.dataset_prob = self.dv.new('shelving_measurement', [('run', 'prob')],
                                        [('Prob', 'dark_prep', 'num')], context=self.prob_context)
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.prob_context)

        self.tt_dark_det_context = self.dv.context()
        self.dv.cd(['', 'shelving_det_timetags_dark_only'], True, context=self.tt_dark_det_context)
        self.tt_dark_det_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                           [('time', 'timetags', 'num')], context=self.tt_dark_det_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_dark_det_context)

        self.tt_dark_dop_context = self.dv.context()
        self.dv.cd(['', 'shelving_dop_timetags_dark_only'], True, context=self.tt_dark_dop_context)
        self.tt_dark_dop_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                           [('time', 'timetags', 'num')], context=self.tt_dark_dop_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_dark_dop_context)

        self.hf_dark_context = self.dv.context()
        self.dv.cd(['', 'shelving_counts_dark_only'], True, context=self.hf_dark_context)
        self.hf_dark_dataset = self.dv.new('counts', [('run', 'arb')],
                                           [('counts', 'detection_counts', 'num'), ('counts', 'doppler_counts', 'num')],
                                           context=self.hf_dark_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hf_dark_context)

    def get_detection_timetags_offset(self):

        op_method = self.p.OpticalPumping.method
        if op_method == 'Standard':
            op_time = self.p.OpticalPumping.duration + self.p.OpticalPumping.extra_repump_time
        elif op_method == 'Both':
            op_time = self.p.OpticalPumping.duration + self.p.OpticalPumping.quadrupole_op_duration + self.p.OpticalPumping.extra_repump_time
        elif op_method == 'QuadrupoleOnly':
            op_time = self.p.OpticalPumping.quadrupole_op_duration + self.p.OpticalPumping.extra_repump_time
            print('You have selected QuadrupoleOnly optical pumping, rethink your choices')

        uW_method = self.p.MicrowaveInterrogation.pulse_sequence
        if uW_method == 'standard':
            uW_duration = self.p.MicrowaveInterrogation.duration + self.p.MicrowaveInterrogation.ttl_switch_delay
        elif uW_method == 'knill':
            uW_duration = 5.0 * self.p.MicrowaveInterrogation.duration + 5.0 * self.p.MicrowaveInterrogation.ttl_switch_delay
        elif uW_method == 'SpinEcho':
            uW_duration = 2.0 * self.p.MicrowaveInterrogation.duration + 3.0 * self.p.MicrowaveInterrogation.ttl_switch_delay
        elif uW_method == 'SuSequence':
            uW_duration = 5.0 * self.p.MicrowaveInterrogation.duration + 2 * U(15.0, 'us')
        elif uW_method == 'DoubleStandard':
            uW_duration = self.p.Pi_times.qubit_0 + self.p.Pi_times.qubit_minus + U(200.0, 'us')
        elif uW_method == 'ClockStandard_KnillZeeman':
            uW_duration = (self.p.Pi_times.qubit_0 + U(2.0, 'us')) + (5 * self.p.Pi_times.qubit_minus + U(4.0, 'us'))
        else:
            uW_duration = U(0.0, 'us')
            print('You have not selected a microwave sequence that is in the timetags offset')


        t_dark = [
            self.p.Shelving_Doppler_Cooling.duration['s'],
            op_time['s'],
            uW_duration['s'],
            self.p.Shelving.duration['s']
        ]

        return sum(t_dark)

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
            popt, pcov = fit(self.lorentzian_fit, detunings[1:], counts[1:], p0=fit_guess)
        except RuntimeError:
            print('Fit did not work, returning RuntimeError from scipy.curve_fit')
            return RuntimeError

        if popt[2] < 200.0:
            return RuntimeError

        center = popt[0]
        return center

    def parse_timetags(self, timetags, doppler_counts, detection_counts):
        """
        Takes in the timetags, doppler counts, and detection counts, and
        parses them into separate lists of doppler and detection counts
        to be saved separately
        """

        detection_timetags = []
        doppler_timetags = []

        for j in range(len(doppler_counts)):
            nDop = doppler_counts[j]
            nDet = detection_counts[j]
            doppler_timetags += list(timetags[:int(nDop)])
            detection_timetags += list(timetags[int(nDop):int(nDet + nDop)])
            timetags = timetags[int(nDop + nDet):]

        return doppler_timetags, detection_timetags

    def lorentzian_fit(self, detuning, center, fwhm, scale, offset):
        """
        This fits a lorentzian in the same format as the fitting routine
        in the RealSimpleGrapher, so that it matches what we get from the
        InterleavedLinescan experiment
        """
        return offset + scale * 0.5 * fwhm / ((detuning - center) ** 2 + (0.5 * fwhm) ** 2)

    def correct_cavity_drift(self):
        center_before = self.run_interleaved_linescan()
        if (center_before == RuntimeError) or (center_before == TypeError):
            return False, 0

        delta = (self.init_line_center - center_before)  # cavity shift in MHz, no labrad units
        j = 0
        while np.abs(delta) > 1.0:
            j += 1
            new_cavity_voltage = self.cavity_voltage + (delta * 0.01)  # 0.01 V/ MHz on cavity
            if np.abs(new_cavity_voltage - self.cavity_voltage) < 0.5:
                self.pzt_server.set_voltage(self.cavity_chan, U(new_cavity_voltage, 'V'))
                self.cavity_voltage = new_cavity_voltage
            else:
                print('Linescan fit did not work, killing tweak up')
                break

            center_after = self.run_interleaved_linescan()
            if (center_after == RuntimeError) or (center_after == TypeError):
                return False, j

            delta = (self.init_line_center - center_after)

        print('Finished cavity tweak up, resuming experiment')
        return True, j

    def sinc_fit(self, freq, omega, center, offset):
        """
        This fits the sinc function created in an interleaved linescan,
        identical to the fit function in RealSimpleGrapher
        """
        return (omega**2/(omega**2 + (center - freq)**2)) * np.sin(np.sqrt(omega**2 + (center - freq)**2)*np.pi/(2*omega))**2 + offset

    def run_microwave_linescan(self, qubit='qubit_minus'):
        self.pulser.line_trigger_state(False)
        self.ttl_server.ttl_output(self.state_detection_ttl_chan, False)
        time.sleep(5)  # make sure the shutter flips

        uW_linescan_context = self.sc.context()

        self.uW_linescan = self.make_experiment(MicrowaveLineScan)
        self.uW_linescan.initialize(self.cxn, uW_linescan_context, self.ident)
        freqs, prob = self.uW_linescan.run(self.cxn, uW_linescan_context)

        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        fit_guess = [5.0, 30.0, 4000.0, 1.0]
        try:
            popt, pcov = fit(self.lorentzian_fit, detunings[1:], counts[1:], p0=fit_guess)
        except RuntimeError:
            print('Fit did not work, returning RuntimeError from scipy.curve_fit')
            return RuntimeError

        if popt[2] < 200.0:
            return RuntimeError

        center = popt[0]
        return center

    def finalize(self, cxn, context):
        # reset the line trigger and delay to false
        self.pulser.line_trigger_state(False)
        self.ttl_server.ttl_output(self.state_detection_ttl_chan, False)
        self.ttl_server.ttl_output(self.protection_beam_ttl_chan, False)



if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = high_fidelity_dark_state_spam(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
