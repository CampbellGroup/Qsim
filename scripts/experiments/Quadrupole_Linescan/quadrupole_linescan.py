import labrad
from Qsim.scripts.pulse_sequences.quadrupole_point import quadrupole_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class QuadrupoleLineScan(QsimExperiment):
    """
    Scan 411nm 
    """

    name = 'Quadrupole Line Scan'

    exp_parameters = []
    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('QuadrupoleLinescan', 'scan'))
    exp_parameters.remove(('QuadrupoleInterrogation', 'detuning'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'probability')
        self.setup_grapher('Quadrupole Linescan')
        self.detunings = self.get_scan_list(self.p.QuadrupoleLinescan.scan, 'kHz')
        center = self.p.Transitions.quadrupole

        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break
            self.p['QuadrupoleInterrogation.detuning'] = U(detuning, 'kHz')
            self.p['Modes.state_detection_mode'] = 'Shelving'
            self.program_pulser(sequence)
            [counts] = self.run_sequence(max_runs=1000, num=1)
            pop = self.get_pop(counts)
            self.dv.add(detuning/1000. + center['MHz'], pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = QuadrupoleLineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
