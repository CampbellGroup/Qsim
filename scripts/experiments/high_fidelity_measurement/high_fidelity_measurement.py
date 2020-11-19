import labrad
from Qsim.scripts.pulse_sequences.shelving_bright_spam import shelving_bright_spam as bright_sequence
from Qsim.scripts.pulse_sequences.shelving_dark_spam import shelving_dark_spam as dark_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.interleaved_linescan.interleaved_linescan import InterleavedLinescan
import numpy as np
from scipy.optimize import curve_fit as fit
from labrad.units import WithUnit as U


class high_fidelity_measurement(QsimExperiment):
    """
    This experiment is similar to the Shelving Fidelity measurement, but with a different organization
    of the pulse sequence and data analysis
    """

    name = 'High Fidelity Measurement'

    exp_parameters = [
        ('Shelving_Doppler_Cooling', 'threshold_std_dev')
    ]
    hidden_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('Shelving_Doppler_Cooling', 'record_timetags'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('MicrowaveInterrogation', 'power'),
        ('Deshelving', 'power1'),
        ('Deshelving', 'power2'),
        ('Deshelving', 'repump_power')
    ]

    exp_parameters.append(('HighFidelityMeasurement', 'sequence_iterations'))

    exp_parameters.extend(bright_sequence.all_required_parameters())
    exp_parameters.extend(dark_sequence.all_required_parameters())

    #for hidden_param in hidden_parameters:
    #    exp_parameters.remove(hidden_param)

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context
        self.pzt_server = cxn.piezo_server
        self.cavity_chan = 1
        self.cavity_voltage = 0.0
        self.hist_mean = 0.0
        self.hist_std_dev = 0.0
        self.doppler_std_dev = 0.0
        self.doppler_mean = 0.0
        self.init_line_center = self.p.Transitions.main_cooling_369['MHz']

    def run(self, cxn, context):

        # set the line trigger state to the appropriate state
        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)
        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
        self.set_fixed_params() # force certain parameters to have fixed values
        self.setup_high_fidelity_datavault() # setup datavault folders for receiving HiFi data
        self.correct_cavity_drift() # make sure that the 369 transition is within 1 MHz of the Transitions parameter

        self.reps = self.p.ShelvingStateDetection.repetitions

        counts_dop_bright = []
        counts_dop_dark = []
        counts_det_bright = []
        counts_det_dark = []
        tt_bright_det = []
        tt_dark_det = []
        tt_bright_dop = []
        tt_dark_dop = []

        i = 0
        while i < self.p.HighFidelityMeasurement.sequence_iterations:
            i += 1

            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            detection_delay_bright, detection_delay_dark = self.get_detection_timetags_offset()

            # programs and runs the bright state sequence, then creates an array with exp number, detection
            # counts, and doppler counts to be saved to datavault
            self.program_pulser(bright_sequence)
            [counts_doppler_bright, counts_bright], ttBright = self.run_sequence_with_timetags(max_runs=250, num=2)

            if (sum(counts_doppler_bright) + sum(counts_bright)) > 30000.0:
                print('Too many timetags, reduce number of experiments')
                break

            ttBright = ttBright[0]
            ttB_dop, ttB_det = self.parse_timetags(ttBright, counts_doppler_bright, counts_bright)
            counts_dop_bright += list(counts_doppler_bright)
            counts_det_bright += list(counts_bright)
            tt_bright_det += list(np.array(ttB_det) - detection_delay_bright)
            tt_bright_dop += list(ttB_dop)


            # programs and runs the dark state sequence, then creates an array with exp number, detection
            # counts, and doppler counts to be saved to datavault
            self.program_pulser(dark_sequence)
            [counts_doppler_dark, counts_dark], ttDark = self.run_sequence_with_timetags(max_runs=250, num=2)

            if (sum(counts_doppler_dark) + sum(counts_dark)) > 30000.0:
                print('Too many timetags, reduce number of experiments')
                break

            ttDark = ttDark[0]
            ttD_dop, ttD_det = self.parse_timetags(ttDark, counts_doppler_dark, counts_dark)

            counts_dop_dark += list(counts_doppler_dark)
            counts_det_dark += list(counts_dark)
            tt_dark_det += list(np.array(ttD_det) - detection_delay_dark)
            tt_dark_dop += list(ttD_dop)

            if i == 1:
                self.doppler_mean = np.mean(counts_doppler_bright)
                self.doppler_std_dev = np.sqrt(np.mean(counts_doppler_bright))

            countsBright, countsDark, n_errors = self.delete_doppler_count_errors(counts_doppler_bright, counts_doppler_dark,
                                                                                  counts_bright, counts_dark)

            # this checks to make sure we didn't lose the ion, effectively, and breaks the loop before a zero division
            # error occurs in plot_prob so that data gets saved
            if (len(countsBright) == 0) or (len(countsDark) == 0):
                print('Ion may have died, zero counts')
                break

            self.plot_prob(i, countsBright, countsDark)
            self.process_histogram(countsBright, countsDark)

            # this part of the loop checks the detection counts to make sure cavity isnt drifting
            if i == 1:
                self.hist_mean = np.mean(countsBright)
                self.hist_std_dev = np.std(countsBright)
                print('mean detection counts on first experiment is  = ' + str(self.hist_mean))
            elif i > 1:
                if np.mean(countsBright) < (self.hist_mean - self.hist_std_dev):
                    self.correct_cavity_drift()
                    self.hist_mean = np.mean(countsBright)
                    self.hist_std_dev = np.std(countsBright)
                    print(str(np.mean(countsBright)) + ' bright state counts, cavity drifting red, killing experiment')
                elif np.mean(countsBright) > (self.hist_mean + self.hist_std_dev):
                    self.correct_cavity_drift()
                    self.hist_mean = np.mean(countsBright)
                    self.hist_std_dev = np.std(countsBright)
                    print(str(np.mean(countsBright)) + ' bright state counts, Cavity drifting blue, killing experiment')

        all_counts = [counts_det_bright, counts_dop_bright, counts_det_dark, counts_dop_dark]
        all_timetags = [tt_bright_det, tt_bright_dop, tt_dark_det, tt_dark_dop]

        self.save_counts_and_timetags(all_counts, all_timetags)

    def process_histogram(self, countsBright, countsDark):
        # process the count_bins and return the histogram with bins and photon counts/bin
        hist_bright = self.process_data(countsBright)
        hist_dark = self.process_data(countsDark)

        # this part plots the histograms on the hist panel in the shelving_fidelity tab
        self.plot_hist(hist_bright, folder_name='Shelving_Histogram')
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

    def plot_prob(self, num, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright,
                        prob_bright - prob_dark, context=self.prob_context)

    def save_counts_and_timetags(self, counts, timetags):
        [counts_bright, counts_doppler_bright, counts_dark, counts_doppler_dark] = counts
        [timetags_det_bright, timetags_dop_bright, timetags_det_dark, timetags_dop_dark] = timetags

        bright_data = np.column_stack((np.arange(len(counts_bright)), np.array(counts_bright), np.array(counts_doppler_bright)))
        self.dv.add(bright_data, context=self.hf_bright_context)
        self.dv.add(np.column_stack((np.zeros(len(timetags_det_bright)), np.array(timetags_det_bright))),
                    context=self.tt_bright_det_context)
        self.dv.add(np.column_stack((np.zeros(len(timetags_dop_bright)), np.array(timetags_dop_bright))),
                    context=self.tt_bright_dop_context)

        dark_data = np.column_stack((np.arange(len(counts_dark)), np.array(counts_dark), np.array(counts_doppler_dark)))
        self.dv.add(dark_data, context=self.hf_dark_context)
        self.dv.add(np.column_stack((np.zeros(len(timetags_det_dark)), np.array(timetags_det_dark))),
                    context=self.tt_dark_det_context)
        self.dv.add(np.column_stack((np.zeros(len(timetags_dop_dark)), np.array(timetags_dop_dark))),
                    context=self.tt_dark_dop_context)

    def delete_doppler_count_errors(self, counts_doppler_bright, counts_doppler_dark, counts_bright, counts_dark):
        """
        takes in the photon counts from each experiment, and the doppler cooling counts for each experiment. Deletes
        the fidelity measurements where the doppler cooling counts were below a user specified threshold
        """

        bright_errors = np.where(counts_doppler_bright <= self.doppler_mean -
                                 self.p.Shelving_Doppler_Cooling.threshold_std_dev * self.doppler_std_dev)
        counts_bright_fixed = np.delete(counts_bright, bright_errors)

        dark_errors = np.where(counts_doppler_dark <= self.doppler_mean -
                               self.p.Shelving_Doppler_Cooling.threshold_std_dev * self.doppler_std_dev)
        counts_dark_fixed = np.delete(counts_dark, dark_errors)

        total_doppler_errors = len(bright_errors[0]) + len(dark_errors[0])
        return counts_bright_fixed, counts_dark_fixed, total_doppler_errors

    def setup_high_fidelity_datavault(self):
        # datavault setup for the run number vs probability plots
        self.prob_context = self.dv.context()
        self.dv.cd(['', 'shelving_probability_vs_runs'], True, context=self.prob_context)

        self.dataset_prob = self.dv.new('shelving_measurement', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')], context=self.prob_context)
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.prob_context)


        # datavault setup for the timetags for bright and dark detection counts in separate folders
        self.tt_bright_det_context = self.dv.context()
        self.dv.cd(['', 'shelving_det_timetags_bright'], True, context=self.tt_bright_det_context)
        self.tt_bright_det_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                             [('time', 'timetags', 'num')], context=self.tt_bright_det_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_bright_det_context)

        self.tt_dark_det_context = self.dv.context()
        self.dv.cd(['', 'shelving_det_timetags_dark'], True, context=self.tt_dark_det_context)
        self.tt_dark_det_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                           [('time', 'timetags', 'num')], context=self.tt_dark_det_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_dark_det_context)

        self.tt_bright_dop_context = self.dv.context()
        self.dv.cd(['', 'shelving_dop_timetags_bright'], True, context=self.tt_bright_dop_context)
        self.tt_bright_dop_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                             [('time', 'timetags', 'num')], context=self.tt_bright_dop_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_bright_dop_context)

        self.tt_dark_dop_context = self.dv.context()
        self.dv.cd(['', 'shelving_dop_timetags_dark'], True, context=self.tt_dark_dop_context)
        self.tt_dark_dop_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                           [('time', 'timetags', 'num')], context=self.tt_dark_dop_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_dark_dop_context)

        # datavault setup for the raw detection counts and doppler counts and experiment number for
        # every experiment performed, bright and dark separately
        self.hf_bright_context = self.dv.context()
        self.dv.cd(['', 'shelving_counts_bright'], True, context=self.hf_bright_context)
        self.hf_bright_dataset = self.dv.new('counts', [('run', 'arb')],
                                             [('counts', 'detection_counts', 'num'), ('counts', 'doppler_counts', 'num')],
                                             context=self.hf_bright_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hf_bright_context)

        self.hf_dark_context = self.dv.context()
        self.dv.cd(['', 'shelving_counts_dark'], True, context=self.hf_dark_context)
        self.hf_dark_dataset = self.dv.new('counts', [('run', 'arb')],
                                           [('counts', 'detection_counts', 'num'), ('counts', 'doppler_counts', 'num')],
                                           context=self.hf_dark_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hf_dark_context)

    def get_detection_timetags_offset(self):

        op_method = self.p.OpticalPumping.method
        if op_method == 'Standard':
            op_time = self.p.OpticalPumping.duration
        elif op_method == 'Both':
            op_time = self.p.OpticalPumping.duration + self.p.OpticalPumping.quadrupole_op_duration + U(100.0, 'us')
        elif op_method == 'QuadrupoleOnly':
            op_time = self.p.OpticalPumping.quadrupole_op_duration
            print('You have selected QuadrupoleOnly optical pumping, rethink your choices')

        uW_method = self.p.MicrowaveInterrogation.pulse_sequence
        if uW_method == 'standard':
            uW_duration = self.p.MicrowaveInterrogation.duration + self.p.MicrowaveInterrogation.ttl_switch_delay
        elif uW_method == 'knill':
            uW_duration = 5.0 * self.p.MicrowaveInterrogation.duration + 5.0 * self.p.MicrowaveInterrogation.ttl_switch_delay
        elif uW_method == 'SpinEcho':
            uW_duration = 2.0 * self.p.MicrowaveInterrogation.duration + 3.0 * self.p.MicrowaveInterrogation.ttl_switch_delay
        else:
            uW_duration = 0.0
            print('You have not selected a microwave sequence that is in the timetags offset')

        t_bright = [
            self.p.Shelving_Doppler_Cooling.duration['s'],
            op_time['s'],
            self.p.Shelving.duration['s']
        ]

        t_dark = [
            self.p.Shelving_Doppler_Cooling.duration['s'],
            op_time['s'],
            uW_duration['s'],
            self.p.Shelving.duration['s']
        ]

        return sum(t_bright), sum(t_dark)

    def parse_timetags(self, timetags, doppler_counts, detection_counts):

        detection_timetags = []
        doppler_timetags = []

        for j in range(len(doppler_counts)):
            nDop = doppler_counts[j]
            nDet = detection_counts[j]
            doppler_timetags += list(timetags[:int(nDop)])
            detection_timetags += list(timetags[int(nDop):int(nDet + nDop)])
            timetags = timetags[int(nDop + nDet):]

        return doppler_timetags, detection_timetags

    def run_interleaved_linescan(self):
        self.pulser.line_trigger_state(False)

        linescan_context = self.sc.context()

        self.line_tracker = self.make_experiment(InterleavedLinescan)
        self.line_tracker.initialize(self.cxn, linescan_context, self.ident)
        detunings, counts = self.line_tracker.run(self.cxn, linescan_context)

        fit_guess = [5.0, 30.0, 4000.0, 1.0]
        popt, pcov = fit(self.lorentzian_fit, detunings, counts, p0=fit_guess)
        center = popt[0]

        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        return center

    def correct_cavity_drift(self):
        center_before = self.run_interleaved_linescan()
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
            delta = (self.init_line_center - center_after)

        print('Finished cavity tweak up, resuming experiment')

    def lorentzian_fit(self, detuning, center, fwhm, scale, offset):
        return offset + scale*0.5*fwhm/((detuning - center)**2 + (0.5*fwhm)**2)

    def finalize(self, cxn, context):
        # reset the line trigger and delay to false
        self.pulser.line_trigger_state(False)



if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = high_fidelity_measurement(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
