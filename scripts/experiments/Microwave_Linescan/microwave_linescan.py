import labrad
from Qsim.scripts.pulse_sequences.microwave_point import microwave_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MicrowaveLineScan(QsimExperiment):
    """
    Scan 12.6 GHz microwave source over the qubit transition
    """

    name = 'Microwave Line Scan'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('Transitions', 'qubit_0'))
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.append(('MicrowaveLinescan', 'scan'))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('MicrowaveInterogation','detuning'))


    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Microwave Linescan')
        self.detunings = self.get_scan_list(self.p.MicrowaveLinescan.scan, 'kHz')
        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break
            self.p['MicrowaveInterogation.detuning'] = U(detuning, 'kHz')
            self.program_pulser(sequence)
            counts = self.run_sequence()
            pop = self.get_pop(counts)
            self.dv.add(detuning, pop)

    def finalize(self, cxn, context):
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveLineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
