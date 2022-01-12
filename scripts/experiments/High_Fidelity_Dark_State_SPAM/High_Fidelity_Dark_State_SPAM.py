import labrad
import numpy as np
from labrad.units import WithUnit as U
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import time as time

from Qsim.scripts.pulse_sequences.shelving_dark_spam import shelving_dark_spam as dark_sequence
from Qsim.scripts.experiments.Interleaved_Linescan.interleaved_linescan import interleaved_linescan
from Qsim.scripts.experiments.Microwave_Linescan.microwave_linescan_minus import MicrowaveLineScanMinus
from Qsim.scripts.experiments.Microwave_Linescan.microwave_linescan_plus import MicrowaveLineScanPlus
from Qsim.scripts.experiments.Microwave_Rabi_Flopping.microwave_rabi_flopping_clock import MicrowaveRabiFloppingClock as rabi_tweak_up


class high_fidelity_dark_state_spam(QsimExperiment):
    """
    This experiment is similar to the high_fidelity_measurement experiment, but attempts to
    make further improvements by adding more drift tracking experiments and potentially trap
    reloading attempts
    """

    name = 'High Fidelity Dark State SPAM'

    exp_parameters = [
        ('HighFidelityMeasurement', 'sequence_iterations')
    ]

    exp_parameters.extend(dark_sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context
        self.pzt_server = cxn.piezo_server
        self.ttl_server = cxn.arduinottl
        self.cavity_chan = 1
        self.cavity_voltage = 0.0
        self.counts_track_mean = 0.0
        self.counts_track_std_dev = 0.0
        self.init_line_center = 0.0
        self.wm_cxn = labrad.connect('10.97.112.2', password='lab')
        self.mp_server = self.wm_cxn.multiplexerserver
        self.dac_port_822 = 3
        self.dac_port_hudson = 1
        self.init_dac_port_822_voltage = 0.0
        self.init_dac_port_hudson_voltage = 0.0


    def run(self, cxn, context):

        # set the line trigger state to the appropriate state
        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        #self.perform_initial_tweak_up()
        break_1, break_2 = self.perform_initial_tweak_up()
        self.set_fixed_params()  # force certain parameters to have fixed values
        self.setup_high_fidelity_datavault()  # setup datavault folders for receiving HiFi data
        self.reps = self.p.ShelvingStateDetection.repetitions

        print('Init DAC voltage is ' + str(self.init_dac_port_822_voltage) + ' mV')

        i = 0
        j = 0
        while True:
            j += 1
            i += 1
            if break_1 or break_2:
                break

            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            self.program_pulser(dark_sequence)
            [counts_doppler_dark, counts_dark] = self.run_sequence(max_runs=500, num=2)

            dac_voltage = self.mp_server.get_output_voltage(self.dac_port_822)
            dac_voltage_hudson = self.mp_server.get_output_voltage(self.dac_port_hudson)
            if (np.abs(dac_voltage - self.init_dac_port_822_voltage) > 200.0) or (np.abs(dac_voltage_hudson - self.init_dac_port_hudson_voltage) > 200.0):
                print('M2 Etalon hopped on experiment ' + str(i) + ', killing experiment.')
                break

            self.save_dark_data([counts_dark, counts_doppler_dark])
            countsDark, countsDopFixed = self.delete_doppler_count_errors(counts_doppler_dark, counts_dark)

            # this checks to make sure we didn't lose the ion, effectively, and breaks the loop before a zero division
            # error occurs in plot_prob so that data gets saved
            if len(countsDark) == 0:
                print('Ion may have died, zero counts')
                break

            self.plot_prob(i, countsDark)
            self.process_histogram(countsDark)

            # this part of the loop checks the doppler counts to make sure cavity isnt drifting

            if i == 1:
                self.counts_track_mean = np.mean(countsDopFixed)
                print('mean doppler counts on first experiment is  = ' + str(self.counts_track_mean))
            elif i > 1:
                diff = np.mean(countsDopFixed) - self.counts_track_mean
                if np.abs(diff) > 7.0:
                    self.cavity_voltage = self.cavity_voltage + np.sign(diff) * 0.005
                    #if np.abs(diff)*0.005 < 0.02:
                    self.pzt_server.set_voltage(self.cavity_chan, U(self.cavity_voltage, 'V'))
                    print('Updated cavity voltage to ' + str(self.cavity_voltage) + ' V')
                else:
                    pass

            if j >= self.p.HighFidelityMeasurement.sequence_iterations:
                break_1, break_2 = self.periodic_tweak_up()
                j = 0

                if break_1 or break_2:
                    break

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

    def perform_initial_tweak_up(self):
        self.init_dac_port_822_voltage = self.mp_server.get_output_voltage(self.dac_port_822)  # gets the init dac port voltage for the M2 lock
        self.init_dac_port_hudson_voltage = self.mp_server.get_output_voltage(self.dac_port_hudson)
        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
        self.run_interleaved_linescan()
        should_break_1 = self.run_microwave_linescan(qubit='qubit_minus')
        should_break_2 = self.run_microwave_linescan(qubit='qubit_plus')
        return should_break_1, should_break_2

    def process_histogram(self, countsDark):
        # process the count_bins and return the histogram with bins and photon counts/bin
        hist_dark = self.process_data(countsDark)

        # this part plots the histograms on the hist panel in the shelving_fidelity tab
        self.plot_hist(hist_dark, folder_name='Shelving_Histogram')

    def set_fixed_params(self):

        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.p['Deshelving.power1'] = self.p.ddsDefaults.repump_760_1_power
        self.p['Deshelving.power2'] = self.p.ddsDefaults.repump_760_2_power
        self.p['Deshelving.repump_power'] = self.p.ddsDefaults.repump_935_power
        self.p['HighFidelityMeasurement.drift_tracking'] = 'On'

    def plot_prob(self, num, counts_dark):
        prob_dark = self.get_pop(counts_dark)
        self.dv.add(num, prob_dark, context=self.prob_context)

    def save_dark_data(self, counts):
        [counts_dark, counts_doppler_dark] = counts

        dark_data = np.column_stack((np.arange(len(counts_dark)), np.array(counts_dark), np.array(counts_doppler_dark)))
        self.dv.add(dark_data, context=self.hf_dark_context)

    def periodic_tweak_up(self):
        self.run_interleaved_linescan()
        self.run_rabi_flop()
        should_break_1 = self.run_microwave_linescan(qubit='qubit_minus')
        should_break_2 = self.run_microwave_linescan(qubit='qubit_plus')
        return should_break_1, should_break_2

    def delete_doppler_count_errors(self, counts_doppler_dark, counts_dark):
        """
        takes in the photon counts from each experiment, and the doppler cooling counts for each experiment. Deletes
        the fidelity measurements where the doppler cooling counts were below a user specified threshold
        """

        dark_errors = np.where(counts_doppler_dark <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
        dark_errors = np.unique(np.concatenate((dark_errors[0], dark_errors[0] - 1.0)))
        counts_dark_fixed = np.delete(counts_dark, dark_errors)
        counts_dop_fixed = np.delete(counts_doppler_dark, dark_errors)

        return counts_dark_fixed, counts_dop_fixed

    def setup_high_fidelity_datavault(self):
        # datavault setup for the run number vs probability plots
        self.prob_context = self.dv.context()
        self.dv.cd(['shelving_fidelity_dark_only', 'shelving_probability_vs_runs'], True, context=self.prob_context)

        self.dataset_prob = self.dv.new('shelving_measurement', [('run', 'prob')],
                                        [('Prob', 'dark_prep', 'num')], context=self.prob_context)
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)

        self.hf_dark_context = self.dv.context()
        self.dv.cd(['shelving_fidelity_dark_only', 'shelving_counts_dark_only'], True, context=self.hf_dark_context)
        self.hf_dark_dataset = self.dv.new('counts', [('run', 'arb')],
                                           [('counts', 'detection_counts', 'num'), ('counts', 'doppler_counts', 'num')],
                                           context=self.hf_dark_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.hf_dark_context)

        self.pi_time_context = self.dv.context()
        self.dv.cd(['shelving_fidelity_dark_only', 'shelving_rabi_tracking'], True, context=self.pi_time_context)
        self.rabi_tracking_dataset = self.dv.new('rabi_tracking', [('time', 's')],
                                                 [('pi_time', '', 'us')], context=self.pi_time_context)


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


    def run_microwave_linescan(self, qubit='qubit_minus'):

        if qubit == 'qubit_minus':
            self.pulser.line_trigger_state(False)
            # gather initial parameters that will need to be reset before resuming main experiment
            init_params = self.p
            uW_minus_context = self.sc.context()
            ###########################################################################

            self.uW_minus = self.make_experiment(MicrowaveLineScanMinus)
            self.uW_minus.initialize(self.cxn, uW_minus_context, self.ident)
            self.uW_minus.run(self.cxn, uW_minus_context)

            if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
                self.pulser.line_trigger_state(True)
                self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

            self.reload_all_parameters()
            self.p = self.parameters

        elif qubit == 'qubit_plus':
            self.pulser.line_trigger_state(False)
            # gather initial parameters that will need to be reset before resuming main experiment
            init_params = self.p
            uW_plus_context = self.sc.context()
            ###########################################################################

            self.uW_plus = self.make_experiment(MicrowaveLineScanPlus)
            self.uW_plus.initialize(self.cxn, uW_plus_context, self.ident)
            self.uW_plus.run(self.cxn, uW_plus_context)

            if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
                self.pulser.line_trigger_state(True)
                self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

            self.reload_all_parameters()
            self.p = self.parameters
            self.p = self.parameters


    def finalize(self, cxn, context):
        # reset the line trigger and delay to false
        self.pulser.line_trigger_state(False)




if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = high_fidelity_dark_state_spam(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
