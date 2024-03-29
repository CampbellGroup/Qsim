import labrad
from Qsim.scripts.pulse_sequences.test_sequence import TestSequence as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class TestPulseSequence(QsimExperiment):
    """
    generic pulse sequence with its own sequence and sub sequence that can be altered 
    to test any particular sequence desired without affecting any other experiment
    """

    name = 'Test Pulse Sequence'

    exp_parameters = []
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('Modes', 'state_detection_mode'))

    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context

    def run(self, cxn, context):

        i = 0
        self.program_pulser(sequence)
        while True:
            should_break = self.update_progress(np.random.rand())
            if should_break:
                break
            [counts0, counts1] = self.run_sequence(max_runs=500, num=2)
            print(counts0, counts1)
            i += 1

    def run_test_sequence(self):
        self.pulser.start_number(100)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        counts = self.pulser.get_readout_counts()
        return counts


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TestPulseSequence(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
