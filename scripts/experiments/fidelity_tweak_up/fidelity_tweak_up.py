import labrad
from Qsim.scripts.pulse_sequences.fidelity_tweak_up import fidelity_tweak_up as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np
from labrad.units import WithUnit as U
import time

class fidelity_tweak_up(QsimExperiment):
    """
    Doppler cool ion the readout bright fidelity,
    readout darkstate and subtract
    """

    name = 'Fidelity Tweak Up'

    exp_parameters = []

    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('MicrowaveInterogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterogation', 'duration'))
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('ShelvingDopplerCooling', 'doppler_counts_threshold'))
    exp_parameters.append(('MLStateDetection', 'repititions'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        qubit = self.p.Line_Selection.qubit
        if qubit == 'qubit_0':
            pi_time = self.p.Pi_times.qubit_0

        elif qubit == 'qubit_plus':
            pi_time = self.p.Pi_times.qubit_plus

        elif qubit == 'qubit_minus':
            pi_time = self.p.Pi_times.qubit_minus

        self.p['MicrowaveInterogation.duration'] = pi_time
        self.p['MicrowaveInterogation.detuning'] = U(0.0, 'kHz')
        self.setup_prob_datavault()
        i = 0
        self.program_pulser(sequence)
        while True:
            i += 1
            if self.p.Modes.state_detection_mode == 'Shelving':
                points_per_hist = self.p.StandardStateDetection.points_per_histogram
                [counts_doppler_bright, counts_bright, counts_doppler_dark, counts_dark] = self.run_sequence(max_runs=250, num=4)
                bright_errors = np.where(counts_doppler_bright <= self.p.ShelvingDopplerCooling.doppler_counts_threshold)
                counts_bright = np.delete(counts_bright, bright_errors)

                dark_errors = np.where(counts_doppler_dark <= self.p.ShelvingDopplerCooling.doppler_counts_threshold)
                counts_dark = np.delete(counts_dark, dark_errors)

                print 'Dark Doppler Errors:', len(dark_errors[0])
                print 'Bright Doppler Errors:', len(bright_errors[0])
                print 'Mean Doppler Counts:', np.mean(counts_doppler_bright)
            elif self.p.Modes.state_detection_mode == 'Standard':
                points_per_hist = self.p.StandardStateDetection.points_per_histogram
                [counts_bright, counts_dark] = self.run_sequence(max_runs=500, num=2)

            elif self.p.Modes.state_detection_mode == 'ML':
                self.timeharp.start_measure(500)
                points_per_hist = self.p.StandardStateDetection.points_per_histogram
                [counts_bright, counts_dark] = self.run_sequence(max_runs=500, num=2)
                time.sleep(1)
                data = self.timeharp.read_fifo(131072)
                stamps = data[0]
                data_length = data[1]
                stamps = stamps[0:data_length]
                timetags = self.convert_timetags(stamps)
                while data_length > 0:
                    data = self.timeharp.read_fifo(131072)
                    stamps = data[0]
                    data_length = data[1]
                    stamps = stamps[0:data_length]
                    timetags += self.convert_timetags(stamps)
                print 'timeharp len', len(timetags), 'Pulser len', np.sum(counts_bright) + np.sum(counts_dark)
                self.timeharp.stop_measure()

            if i % points_per_hist == 0:
                hist_bright = self.process_data(counts_bright)
                #print hist_bright
                hist_dark = self.process_data(counts_dark)
                self.plot_hist(hist_bright)
                self.plot_hist(hist_dark)
            self.plot_prob(i, counts_bright, counts_dark)
            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                self.program_pulser(sequence)

    def setup_prob_datavault(self):
        self.dv.cd(['', 'fidelity_tweak_up'], True)

        self.dataset_prob = self.dv.new('fidelity_tweak_up', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')])
        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

    def plot_prob(self, num, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright,
                    prob_bright - prob_dark)


        
if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = fidelity_tweak_up(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
