import labrad
from Qsim.scripts.pulse_sequences.test_sequence import TestSequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
# from labrad.units import WithUnit as U
import numpy as np


class TestPulseSequence(QsimExperiment):
    """
    Generic experiment (sublclassed from QsimExperiment) with its own sequence and sub-sequence that can be altered
    to test any particular sequence desired without affecting any other experiment
    """

    name = 'Test Pulse Sequence'

    exp_parameters = []
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('Modes', 'state_detection_mode'))

    exp_parameters.extend(TestSequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context

    def run(self, cxn, context):

        i = 0
        self.program_pulser(TestSequence)
        while True:
            should_break = self.update_progress(np.random.rand())
            if should_break:
                break
            self.run_sequence()
            print(i)
            i += 1


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TestPulseSequence(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
