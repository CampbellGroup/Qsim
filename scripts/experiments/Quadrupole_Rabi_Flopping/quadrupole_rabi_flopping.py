import labrad
from Qsim.scripts.pulse_sequences.quadrupole_point import quadrupole_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class QuadrupoleRabiFlopping(QsimExperiment):
    """

    """

    name = 'Quadrupole Rabi Flopping'

    exp_parameters = []
    exp_parameters.append(('QuadrupoleRabiFlopping', 'scan'))
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('QuadrupoleInterrogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.p['Modes.state_detection_mode'] = 'Standard'
        self.p['MicrowaveInterrogation.duration'] = self.p.Pi_times.qubit_0
        self.setup_datavault('time', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Quadrupole Rabi Flopping')
        self.times = self.get_scan_list(self.p.QuadrupoleRabiFlopping.scan, 'us')
        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break
            self.p['QuadrupoleInterrogation.duration'] = U(duration, 'us')
            self.program_pulser(sequence)
            [counts] = self.run_sequence(max_runs=1000, num=1)
            hist = self.process_data(counts)
            self.plot_hist(hist)
            pop = self.get_pop(counts)
            self.dv.add(duration, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = QuadrupoleRabiFlopping(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
