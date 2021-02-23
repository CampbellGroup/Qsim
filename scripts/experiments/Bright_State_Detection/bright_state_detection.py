import labrad
from Qsim.scripts.pulse_sequences.bright_state_preparation import bright_state_preparation as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.experiments.interleaved_linescan.interleaved_linescan import InterleavedLinescan
from scipy.optimize import curve_fit as fit
import numpy as np
from labrad.units import WithUnit as U

class BrightStateDetection(QsimExperiment):
    """
    Perform preparation of the bright state for either shelving or standard detection,
    and plot histograms and readout fidelity of the bright state continuously
    """

    name = 'Bright State Detection'

    exp_parameters = []
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = self.cxn.pulser
        self.rsg = self.cxn.grapher
        self.pzt_server = cxn.piezo_server
        self.prob_ctx = self.dv.context()
        self.hist_ctx = self.dv.context()
        self.cavity_chan = 1
        self.cavity_voltage = 0.0
        self.hist_mean = 0.0
        self.hist_std_dev = 0.0

    def run(self, cxn, context):
        mode = self.p.Modes.state_detection_mode
        threshold = self.p.ShelvingStateDetection.state_readout_threshold
        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
        self.init_line_center = self.run_interleaved_linescan()
        self.pv.set_parameter(('Transitions', 'main_cooling_369', U(self.init_line_center, 'MHz')))

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
                bright_dataset = np.column_stack((np.arange(len(counts)), np.array(counts), np.array(doppler_counts)))
                self.dv.add(bright_dataset, context=self.bright_state_counts)

                detection_errors = np.where(counts < threshold)
                doppler_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                counts = np.delete(counts, doppler_errors)
                print('Mean detection counts on experiment ' + str(i) + ' = ' + str(np.mean(counts)))
                if len(detection_errors[0]) > 0.0:
                    print("Detection error on experiments " + str(detection_errors[0]) + ", with doppler counts " + str(doppler_counts[detection_errors]) + " where mean doppler counts were " + str(np.mean(doppler_counts)))
                    try:
                        print("Doppler counts before error = " + str(doppler_counts[detection_errors[0] - 1]))
                        print("Doppler counts after error = " + str(doppler_counts[detection_errors[0] + 1]))
                    except IndexError:
                        pass

            # run and process data if detection mode is standard
            elif mode == 'Standard':
                [counts] = self.run_sequence(max_runs=1000)

            # process counts into a histogram and plot on grapher
            if i % points_per_hist == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist, folder_name='Bright_State_Detection')

            self.plot_prob(i, counts)
            if mode == 'Shelving':
                if i == 1:
                    self.hist_mean = np.mean(counts)
                    self.hist_std_dev = np.sqrt(np.mean(counts))
                    print('mean detection counts on first experiment is  = ' + str(self.hist_mean))
                elif i > 1:
                    diff = np.mean(counts) - self.hist_mean
                    if np.abs(diff) > 5.0:
                        self.cavity_voltage = self.cavity_voltage + np.sign(diff)*0.005
                        self.pzt_server.set_voltage(self.cavity_chan, U(self.cavity_voltage, 'V'))
                        print('Updated cavity voltage to ' + str(self.cavity_voltage) + ' V')
                    else:
                        pass
                    #if (np.mean(counts) < (self.hist_mean - self.hist_std_dev)) or (
                    #        np.mean(counts) > (self.hist_mean + self.hist_std_dev)):
                    #    success, iterations = self.correct_cavity_drift()
                    #    if success & iterations == 1:
                    #        print('Cavity was fine, updating mean counts and std deviation')
                    #        self.hist_mean = np.mean(counts)
                    #        self.hist_std_dev = np.std(counts)
                    #    elif success & iterations != 1:
                    #        pass
                    #    else:
                    #        break

            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                    self.program_pulser(sequence)


    def setup_prob_datavault(self):
        self.dv.cd(['', 'Bright_State_Probability'],
                   True, context=self.prob_ctx)
        self.dataset_prob = self.dv.new('fidelity_bright_state_prep',
                                        [('run', 'arb u')],
                                        [('Counts', 'Counts', 'num')],
                                        context=self.prob_ctx)

        self.rsg.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.prob_ctx)

        self.bright_state_counts = self.dv.context()
        self.dv.cd(['', 'Bright_State_Counts'], True, context=self.bright_state_counts)
        self.bright_state_counts_dataset = self.dv.new('bright_state_counts', [('run', 'arb')],
                                                       [('counts', 'detection_counts', 'num'), ('counts', 'doppler_counts', 'num')],
                                                       context=self.bright_state_counts)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.bright_state_counts)

    def run_interleaved_linescan(self):
        self.pulser.line_trigger_state(False)

        linescan_context = self.sc.context()

        self.line_tracker = self.make_experiment(InterleavedLinescan)
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
                return False

            self.pv.set_parameter(('Transitions', 'main_cooling_369', U(center_after, 'MHz')))
            delta = (self.init_line_center - center_after)

        print('Finished cavity tweak up, resuming experiment')
        return True, j

    def plot_prob(self, num, counts):
        prob = self.get_pop(counts)
        self.dv.add(num, prob, context=self.prob_ctx)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = BrightStateDetection(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
