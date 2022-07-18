import labrad
from Qsim.scripts.pulse_sequences.microwave_point.metastable_microwave_point_173 \
    import MetastableMicrowavePoint173 as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MetastableMicrowaveLineScan173(QsimExperiment):
    """
    Scan microwave source over a qubit transition in the F7/2
    state. There are different ways of running this experiment as well,
    like with heralded state preparation or not
    """

    name = 'Metastable Microwave Line Scan 173'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('MetastableMicrowaveLinescan173', 'scan'))
    exp_parameters.append(('Pi_times', 'metastable_qubit_173'))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.append(('MetastableStateDetection', 'repetitions'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Metastable Microwave Linescan')
        self.detunings = self.get_scan_list(self.p.MetastableMicrowaveLinescan173.scan, 'kHz')

        self.p['Metastable_Microwave_Interrogation.duration'] = self.p.Pi_times.metastable_qubit_173
        self.p['Modes.state_detection_mode'] = 'Shelving'

        print(self.p['Metastable_Microwave_Interrogation.duration'])

        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break
            self.p['Metastable_Microwave_Interrogation.detuning'] = U(detuning, 'kHz')
            self.program_pulser(sequence)
            [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
            errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            counts = np.delete(detection_counts, errors)

            hist = self.process_data(counts)
            self.plot_hist(hist)
            pop = self.get_pop(counts)

            self.dv.add(detuning + self.p.Transitions.MetastableQubit['kHz'], pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    experiment = MetastableMicrowaveLineScan173(cxn=cxn)
    ident = scanner.register_external_launch(experiment.name)
    experiment.execute(ident)
