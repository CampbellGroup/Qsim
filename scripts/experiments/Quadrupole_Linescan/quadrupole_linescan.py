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
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        self.setup_datavault('frequency', 'probability')
        self.setup_grapher('Quadrupole Linescan')
        self.detunings = self.get_scan_list(self.p.QuadrupoleLinescan.scan, 'kHz')
        center = self.p.Transitions.quadrupole
        self.p['Line_Selection.qubit'] = 'qubit_0'
        self.p['MicrowaveInterrogation.duration'] = self.p.Pi_times.qubit_0

        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break
            self.p['QuadrupoleInterrogation.detuning'] = U(detuning, 'kHz')
            self.program_pulser(sequence)
            [counts] = self.run_sequence(max_runs=1000, num=1)
            pop = self.get_pop(counts)
            hist = self.process_data(counts)
            self.plot_hist(hist)
            self.dv.add(detuning/1000. + center['MHz'], pop)

    def finalize(self, cxn, context):
        self.pulser.line_trigger_state(False)
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = QuadrupoleLineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
