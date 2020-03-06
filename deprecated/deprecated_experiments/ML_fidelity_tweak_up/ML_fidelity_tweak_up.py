import labrad
from Qsim.scripts.pulse_sequences.ML_bright_state_preparation import ML_bright_state_preparation as bright_prep_seq
from Qsim.scripts.pulse_sequences.ML_dark_state_preparation import ML_dark_state_preparation as dark_prep_seq
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np
from labrad.units import WithUnit as U
import time


class ML_fidelity_tweak_up(QsimExperiment):
    """
    Doppler cool ion the readout bright fidelity,
    readout darkstate and subtract
    """

    name = 'ML Fidelity Tweak Up'

    exp_parameters = []

    # add parameters that we want to set
    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))
    exp_parameters.append(('MLStateDetection', 'repititions'))
    exp_parameters.append(('MLStateDetection', 'points_per_histogram'))
    exp_parameters.append(('MLStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('MLStateDetection', 'save_timetags'))
    exp_parameters.append(('bf_fluorescence', 'crop_start_time'))
    exp_parameters.append(('bf_fluorescence', 'crop_stop_time'))
    exp_parameters.append(('Modes', 'state_detection_mode'))

    exp_parameters.extend(bright_prep_seq.all_required_parameters())
    exp_parameters.extend(dark_prep_seq.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.cropped_ctx = self.cxn.data_vault.context()
        self.rawData_ctx = self.cxn.data_vault.context()
        self.timetags_bright_ctx = self.cxn.data_vault.context()
        self.timetags_dark_ctx = self.cxn.data_vault.context()

    def run(self, cxn, context):

        self.setup_prob_datavault()

        i = 0
        while True:
            i += 1
            points_per_hist = self.p.MLStateDetection.points_per_histogram
            self.program_pulser(bright_prep_seq)
            self.method = 'bright'
            [counts_bright_cropped, counts_bright_all, timetags_bright] = self.run_ML_sequence()
            self.program_pulser(dark_prep_seq)
            self.method = 'dark'
            [counts_dark_cropped, counts_dark_all, timetags_dark] = self.run_ML_sequence()

            if i % points_per_hist == 0:
                hist_bright = self.process_data(counts_bright_cropped)
                hist_dark = self.process_data(counts_dark_cropped)
                self.plot_hist(hist_bright)
                self.plot_hist(hist_dark)

            self.plot_prob(i, counts_bright_cropped, counts_dark_cropped, context=self.cropped_ctx)
            should_break = self.update_progress(np.random.random())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters

    def run_ML_sequence(self, max_runs=1000, num=1):
        reps = self.p.MLStateDetection.repititions
        counts = np.array([])
        allCounts = np.array([])
        low = self.p.bf_fluorescence.crop_start_time['ns']
        high = self.p.bf_fluorescence.crop_stop_time['ns']

        for iteration in range(int(reps)):
            self.timeharp.start_measure(60000)
            self.pulser.start_number(1)
            self.pulser.wait_sequence_done()
            self.timeharp.stop_measure()
            data = self.timeharp.read_fifo(2048)
            stamps = data[0]
            data_length = data[1]
            stamps = stamps[0:data_length]
            timetags = self.convert_timetags(stamps)
            #if self.method == 'bright':
            #    self.parse_timetags(timetags, context=self.timetags_bright_ctx)
            #if self.method == 'dark':
            #    self.parse_timetags(timetags, context=self.timetags_dark_ctx)
            cropped_timetags = sum([low <= item <= high for item in timetags])
            all_timetags = sum([0.0 <= item <= 12.5 for item in timetags])
            counts = np.concatenate((counts, np.array([cropped_timetags])))
            allCounts = np.concatenate((allCounts, np.array([all_timetags])))
        self.pulser.stop_sequence()
        return [counts, allCounts, timetags]

    def setup_prob_datavault(self):

        self.dv.cd(['', 'ML_fidelity_tweak_up_CROPPED'], True, context=self.cropped_ctx)

        self.dataset_prob = self.dv.new('ML_fidelity_tweak_up', [('run', 'prob')],
                                        [('Prob', 'bright_prep', 'num'),
                                         ('Prob', 'dark_prep', 'num'),
                                         ('Prob', 'contrast', 'num')], context=self.cropped_ctx)

        self.dv.cd(['', 'ML_fidelity_tweak_up_RAW'], True, context=self.rawData_ctx)

        self.dataset_raw = self.dv.new('ML_fidelity_tweak_up', [('run', 'prob')],
                                       [('Prob', 'bright_prep', 'num'),
                                        ('Prob', 'dark_prep', 'num'),
                                        ('Prob', 'contrast', 'num')], context=self.rawData_ctx)

        self.dv.cd(['', 'ML_fidelity_tweak_up_timetags_bright'], True, context=self.timetags_bright_ctx)

        self.dataset_timetags_bright = self.dv.new('ML_fidelity_tweak_up', [('time_bin', 'num')],
                                       [('Photons','counts', 'num')], context=self.timetags_bright_ctx)

        self.dv.cd(['', 'ML_fidelity_tweak_up_timetags_dark'], True, context=self.timetags_dark_ctx)

        self.dataset_timetags_dark = self.dv.new('ML_fidelity_tweak_up', [('time_bin', 'num')],
                                       [('Photons','counts', 'num')], context=self.timetags_dark_ctx)

        self.grapher.plot(self.dataset_prob, 'Fidelity', False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.cropped_ctx)

    def plot_prob(self, num, counts_bright, counts_dark, context):
        #num_dark = np.sum(counts_dark)
        #num_bright = np.sum(counts_bright)
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright,
                    prob_bright - prob_dark, context=context)

    def parse_timetags(self, timetags, context):
        timetags = 1000*np.array(timetags)
        time_bins = np.arange(0.0, 13000, 25)
        counts, bins = np.histogram(timetags, time_bins)
        print 'parse_timetags'
        for j in range(len(counts)):
            self.dv.add(bins[j], counts[j], context=context)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ML_fidelity_tweak_up(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
