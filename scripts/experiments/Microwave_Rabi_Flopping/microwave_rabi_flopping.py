import labrad
from Qsim.scripts.pulse_sequences.microwave_point import microwave_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MicrowaveRabiFlopping(QsimExperiment):
    """
    Scan the 369 laser with the AOM double pass interleaved
    with doppler cooling.
    """

    name = 'Microwave Rabi Flopping'

    exp_parameters = []
    exp_parameters.append(('RabiFlopping', 'scan'))
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection','repititions'))
    exp_parameters.append(('StandardStateDetection','repititions'))
    exp_parameters.append(('StandardStateDetection','points_per_histogram'))
    exp_parameters.append(('StandardStateDetection','state_readout_threshold'))
    exp_parameters.append(('ShelvingDopplerCooling','doppler_counts_threshold'))
    exp_parameters.append(('MLStateDetection','repititions'))


    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('MicrowaveInterogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('time', 'probability')  # gives the x and y names to Data Vault
        qubit = self.p.Line_Selection.qubit
        mode = self.p.Modes.state_detection_mode
        self.setup_grapher('Rabi Flopping ' + qubit)
        self.times = self.get_scan_list(self.p.RabiFlopping.scan, 'us')
        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break
            self.p['MicrowaveInterogation.duration'] = U(duration, 'us')
            self.program_pulser(sequence)
            if mode == 'Shelving':
                [doppler_counts, detection_counts] = self.run_sequence(max_runs = 500, num = 2)
                errors = np.where(doppler_counts <= self.p.ShelvingDopplerCooling.doppler_counts_threshold)
                counts = np.delete(detection_counts, errors)
            else:
                [counts] = self.run_sequence()
            if i % self.p.StandardStateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)
            pop = self.get_pop(counts)
            self.dv.add(duration, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveRabiFlopping(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
