import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.doppler_cooling_leakthrough_test import doppler_cooling_leakthrough_test as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U


class doppler_cooling_leakthrough_test(QsimExperiment):
    """
    this experiment will prepare the 0 state, then wait for a varying amount of time, and detect population in
    the 1 state either via shelving or standard state detection
    """

    name = 'DopplerCoolingLeakthroughTest'

    exp_parameters = []

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('EmptySequence', 'scan_empty_duration'))
    exp_parameters.remove(('DoublePass369', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.setup_datavault('time', 'probability')
        self.setup_grapher('DopplerCoolingLeakthroughTest')
        self.times = self.get_scan_list(self.p.EmptySequence.scan_empty_duration, 'us')
        for i, duration in enumerate(self.times):

            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break

            self.p['DoublePass369.duration'] = U(duration, 'us')

            if self.p.Modes.state_detection_mode == 'Standard':
                self.program_pulser(sequence)
                [counts] = self.run_sequence(num=1, max_runs=1000)

            elif self.p.Modes.state_detection_mode == 'Shelving':
                self.program_pulser(sequence)
                [doppler_counts, counts] = self.run_sequence(num=2, max_runs=500)
                doppler_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                counts = np.delete(counts, doppler_errors)

            hist = self.process_data(counts)
            self.plot_hist(hist)
            pop = self.get_pop(counts)
            self.dv.add(duration, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = doppler_cooling_leakthough_test(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
