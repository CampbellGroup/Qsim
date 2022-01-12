import labrad
from Qsim.scripts.pulse_sequences.shelving_bright_spam import shelving_bright_spam as bright_sequence
from Qsim.scripts.pulse_sequences.shelving_dark_spam import shelving_dark_spam as dark_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.Interleaved_Linescan.interleaved_linescan import interleaved_linescan
from Qsim.scripts.experiments.Microwave_Rabi_Flopping.microwave_rabi_flopping_clock import MicrowaveRabiFloppingClock as rabi_tweak_up
import numpy as np
from scipy.optimize import curve_fit as fit
from labrad.units import WithUnit as U
import time


class high_fidelity_measurement(QsimExperiment):
    """
    This experiment is similar to the Shelving Fidelity measurement, but with a different organization
    of the pulse sequence and data analysis
    """

    name = 'High Fidelity Measurement'

    exp_parameters = [
        ('HighFidelityMeasurement', 'sequence_iterations')
    ]


    exp_parameters.extend(bright_sequence.all_required_parameters())
    exp_parameters.extend(dark_sequence.all_required_parameters())


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context
        self.pzt_server = cxn.piezo_server
        self.cavity_chan = 1
        self.cavity_voltage = 0.0
        self.hist_mean = 0.0
        self.hist_std_dev = 0.0
        self.wm_cxn = labrad.connect('10.97.112.2', password='lab')
        self.mp_server = self.wm_cxn.multiplexerserver
        self.dac_port_822 = 3
        self.init_dac_port_822_voltage = 0.0
        self.counts_track_mean = 0.0

    def run(self, cxn, context):
        self.setup_high_fidelity_datavault()  # setup datavault folders for receiving HiFi data

        self.init_dac_port_822_voltage = self.mp_server.get_output_voltage(self.dac_port_822) #  gets the init dac port voltage for the M2 lock
        print('Init DAC voltage is ' + str(self.init_dac_port_822_voltage) + ' mV')

        # set the line trigger state to the appropriate state
        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)
        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)

        self.run_interleaved_linescan()
        self.run_rabi_flop()

        self.set_fixed_params()  # force certain parameters to have fixed values
        self.reps = self.p.ShelvingStateDetection.repetitions


        i = 0
        n_exp = 0
        while True:

            i += 1
            n_exp += 2 * self.p.ShelvingStateDetection.repetitions

            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            detection_delay_bright, detection_delay_dark = self.get_detection_timetags_offset()


            self.program_pulser(bright_sequence)
            [counts_doppler_bright, counts_bright], ttBright = self.run_sequence_with_timetags(max_runs=250, num=2)
            dac_voltage = self.mp_server.get_output_voltage(self.dac_port_822)

            if np.abs(dac_voltage - self.init_dac_port_822_voltage) > 200.0:
                print('M2 Etalon hopped on experiment ' + str(i) + ', killing experiment.')
                break

            if (sum(counts_doppler_bright) + sum(counts_bright)) > 30000.0:
                print('Too many timetags, reduce number of experiments')
                break

            ttBright = ttBright[0]
            ttB_dop, ttB_det = self.parse_timetags(ttBright, counts_doppler_bright, counts_bright)
            ttB_det = np.array(ttB_det) - detection_delay_bright
            self.save_bright_data([counts_bright, counts_doppler_bright], [ttB_det, ttB_dop])

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

            countsBright, countsDark, n_errors = self.delete_doppler_count_errors(counts_doppler_bright, counts_doppler_dark,
                                                                                  counts_bright, counts_dark)

            # this checks to make sure we didn't lose the ion, effectively, and breaks the loop before a zero division
            # error occurs in plot_prob so that data gets saved
            if (len(countsBright) < 5) or (len(countsDark) < 5):
                print('Ion may have died')
                break

            self.cavity_tweak_up(i, countsBright)
            self.plot_prob(i, countsBright, countsDark)
            self.process_histogram(countsBright, countsDark)

            if n_exp >= 2000.:
                self.run_interleaved_linescan()
                self.run_rabi_flop()
                n_exp = 0

    def run_rabi_flop(self):

        init_params = self.p

        self.pulser.line_trigger_state(False)
        rabi_context = self.sc.context()
        self.rabi_tracker = self.make_experiment(rabi_tweak_up)
        self.rabi_tracker.initialize(self.cxn, rabi_context, self.ident)
        pi_time = self.rabi_tracker.run(self.cxn, rabi_context)

        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        self.p = init_params
        self.pv.set_parameter(('Pi_times', 'qubit_0', U(pi_time, 'us')))
        self.pv.set_parameter(('MicrowaveInterrogation', 'duration', U(pi_time, 'us')))

        # save rabi tracking data
        self.dv.add(pi_time, time.time(), context=self.pi_time_context)

        self.reload_all_parameters()
        self.p = self.parameters



    def run_interleaved_linescan(self):

        init_params = self.p

        self.pulser.line_trigger_state(False)

        linescan_context = self.sc.context()
        self.line_tracker = self.make_experiment(interleaved_linescan)
        self.line_tracker.initialize(self.cxn, linescan_context, self.ident)
        self.line_tracker.run(self.cxn, linescan_context)

        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        self.reload_all_parameters()
        self.p = self.parameters
        print(self.p['Transitions.main_cooling_369'])


    def process_histogram(self, countsBright, countsDark):
        # process the count_bins and return the histogram with bins and photon counts/bin
        hist_bright = self.process_data(countsBright)
        hist_dark = self.process_data(countsDark)

        # this part plots the histograms on the hist panel in the shelving_fidelity tab
        self.plot_hist(hist_bright, folder_name='Shelving_Histogram')
        self.plot_hist(hist_dark, folder_name='Shelving_Histogram')

    def cavity_tweak_up(self, i, countsBright):
        if i == 1:
            self.counts_track_mean = np.mean(countsBright)
            print('mean bright detection counts on first experiment experiment is  = ' + str(self.counts_track_mean))
        elif i >= 2:
            diff = np.mean(countsBright) - self.counts_track_mean
            if np.abs(diff) > 10.0:
                self.cavity_voltage = self.cavity_voltage + np.sign(diff) * 0.005
                if np.sign(diff) * 0.005 < 0.2:
                    self.pzt_server.set_voltage(self.cavity_chan, U(self.cavity_voltage, 'V'))
                    print('Updated cavity voltage to ' + str(self.cavity_voltage) + ' V')
            else:
                pass

    def set_fixed_params(self):
        self.p['Line_Selection.qubit'] = 'qubit_0'
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


    def save_bright_data(self, counts, timetags):
        [counts_bright, counts_doppler_bright] = counts
        [timetags_det_bright, timetags_dop_bright] = timetags

        bright_data = np.column_stack(
            (np.arange(len(counts_bright)), np.array(counts_bright), np.array(counts_doppler_bright)))
        self.dv.add(bright_data, context=self.hf_bright_context)
        self.dv.add(np.column_stack((np.zeros(len(timetags_det_bright)), np.array(timetags_det_bright))),
                    context=self.tt_bright_det_context)
        self.dv.add(np.column_stack((np.zeros(len(timetags_dop_bright)), np.array(timetags_dop_bright))),
                    context=self.tt_bright_dop_context)

    def save_dark_data(self, counts, timetags):
        [counts_dark, counts_doppler_dark] = counts
        [timetags_det_dark, timetags_dop_dark] = timetags

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

        THIS CURRENTLY IMPLEMENTS STORAGE ERRORS
        """

        bright_errors = np.where(counts_doppler_bright <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
        bright_errors = np.unique(np.concatenate((bright_errors[0], bright_errors[0] - 1)))
        counts_bright_fixed = np.delete(counts_bright, bright_errors)

        dark_errors = np.where(counts_doppler_dark <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
        dark_errors = np.unique(np.concatenate((dark_errors[0], dark_errors[0] - 1)))
        counts_dark_fixed = np.delete(counts_dark, dark_errors)

        total_doppler_errors = len(bright_errors) + len(dark_errors)
        return counts_bright_fixed, counts_dark_fixed, total_doppler_errors

    def setup_high_fidelity_datavault(self):
        # datavault setup for the run number vs probability plots
        self.prob_context = self.dv.context()
        self.dv.cd(['shelving_fidelity', 'shelving_probability_vs_runs'], True, context=self.prob_context)

        self.dataset_prob = self.dv.new('shelving_measurement', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')], context=self.prob_context)
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.prob_context)


        # datavault setup for the timetags for bright and dark detection counts in separate folders
        self.tt_bright_det_context = self.dv.context()
        self.dv.cd(['shelving_fidelity', 'shelving_det_timetags_bright'], True, context=self.tt_bright_det_context)
        self.tt_bright_det_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                             [('time', 'timetags', 'num')], context=self.tt_bright_det_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_bright_det_context)

        self.tt_dark_det_context = self.dv.context()
        self.dv.cd(['shelving_fidelity', 'shelving_det_timetags_dark'], True, context=self.tt_dark_det_context)
        self.tt_dark_det_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                           [('time', 'timetags', 'num')], context=self.tt_dark_det_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_dark_det_context)

        self.tt_bright_dop_context = self.dv.context()
        self.dv.cd(['shelving_fidelity', 'shelving_dop_timetags_bright'], True, context=self.tt_bright_dop_context)
        self.tt_bright_dop_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                             [('time', 'timetags', 'num')], context=self.tt_bright_dop_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_bright_dop_context)

        self.tt_dark_dop_context = self.dv.context()
        self.dv.cd(['shelving_fidelity', 'shelving_dop_timetags_dark'], True, context=self.tt_dark_dop_context)
        self.tt_dark_dop_dataset = self.dv.new('timetags', [('arb', 'arb')],
                                           [('time', 'timetags', 'num')], context=self.tt_dark_dop_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.tt_dark_dop_context)

        # datavault setup for the raw detection counts and doppler counts and experiment number for
        # every experiment performed, bright and dark separately
        self.hf_bright_context = self.dv.context()
        self.dv.cd(['shelving_fidelity', 'shelving_counts_bright'], True, context=self.hf_bright_context)
        self.hf_bright_dataset = self.dv.new('counts', [('run', 'arb')],
                                             [('counts', 'detection_counts', 'num'), ('counts', 'doppler_counts', 'num')],
                                             context=self.hf_bright_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hf_bright_context)

        self.hf_dark_context = self.dv.context()
        self.dv.cd(['shelving_fidelity', 'shelving_counts_dark'], True, context=self.hf_dark_context)
        self.hf_dark_dataset = self.dv.new('counts', [('run', 'arb')],
                                           [('counts', 'detection_counts', 'num'), ('counts', 'doppler_counts', 'num')],
                                           context=self.hf_dark_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hf_dark_context)

        self.pi_time_context = self.dv.context()
        self.dv.cd(['shelving_fidelity', 'shelving_rabi_tracking'], True, context=self.pi_time_context)
        self.rabi_tracking_dataset = self.dv.new('rabi_tracking', [('time', 's')],
                                                 [('pi_time','', 'us')], context=self.pi_time_context)

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
            uW_duration = self.p.Pi_times.qubit_0 + self.p.Pi_times.qubit_plus + U(200.0, 'us')
        else:
            uW_duration = U(0.0, 'us')
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


    def finalize(self, cxn, context):
        # reset the line trigger and delay to false
        self.pulser.line_trigger_state(False)



if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = high_fidelity_measurement(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
