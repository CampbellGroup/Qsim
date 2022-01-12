import labrad
import numpy as np
from labrad.units import WithUnit as U
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.pulse_sequences.sf_discrimination_sequence import sf_discrimination_sequence as sequence


class sf_discrimination_experiment(QsimExperiment):

    name = 'SF Discrimination Experiment'

    exp_parameters = [
        ('StandardStateDetection', 'repetitions'),
        ('Modes', 'state_detection_mode')
    ]

    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.context = context
        self.pzt_server = cxn.piezo_server
        self.cavity_chan = 1
        self.cavity_voltage = 0.0
        self.counts_track_mean = 0.0
        self.counts_track_std_dev = 0.0

    def run(self, cxn, context):
        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_chan)
        self.setup_sf_datavault()
        previous_exp_mean = 0.0

        i = 0
        while True:
            i += 1
            should_break = self.update_progress(np.random.random())
            if should_break:
                break

            self.program_pulser(sequence)
            [counts] = self.run_sequence(max_runs=1000, num=1)
            if (np.mean(counts) < 0.9*previous_exp_mean) and i != 1:
                break
            previous_exp_mean = np.mean(counts)
            print('Mean counts on last experiment = ' + str(np.mean(counts)))
            self.save_data(counts)

            if i == 1:
                self.counts_track_mean = np.mean(counts)
                print('mean counts on first experiment is  = ' + str(self.counts_track_mean))
            elif i > 1:
                diff = np.mean(counts) - self.counts_track_mean
                if np.abs(diff) > 2.0:
                    self.cavity_voltage = self.cavity_voltage + np.sign(diff) * 0.005
                    if np.sign(diff)*0.005 < 0.2:
                        self.pzt_server.set_voltage(self.cavity_chan, U(self.cavity_voltage, 'V'))
                        print('Updated cavity voltage to ' + str(self.cavity_voltage) + ' V')
                else:
                    pass

    def process_histogram(self, counts):
        hist = self.process_data(counts)
        self.plot_hist(hist, folder_name='Histograms')

    def save_data(self, counts):
        counts_data = np.column_stack((np.arange(len(counts)), np.array(counts)))
        self.dv.add(counts_data, context=self.counts_context)

    def setup_sf_datavault(self):
        self.counts_context = self.dv.context()
        self.dv.cd(['', 'SF_Discrimination'], True, context=self.counts_context)
        self.hf_dark_dataset = self.dv.new('counts', [('run', 'arb')],
                                           [('counts', 'detection_counts', 'num')],
                                           context=self.counts_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.counts_context)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = sf_discrimination_experiment(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
