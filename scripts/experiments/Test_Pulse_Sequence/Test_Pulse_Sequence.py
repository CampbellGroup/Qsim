import labrad
from Qsim.scripts.pulse_sequences.test_sequence import test_sequence as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit
import numpy as np

class TestPulseSequence(QsimExperiment):
    """
    generic pulse sequence with its own sequence and sub sequence that can be altered 
    to test any partiular sequence desired without affecting any other experiment
    """

    name = 'Test Pulse Sequence'

    exp_parameters = []
    exp_parameters.append(('TestSequence','duration'))
    exp_parameters.append(('EmptySequence','duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.reg = cxn.registry
        self.reg.cd(['', 'settings'])
        self.pulser = cxn.servers['pulser']

    def run (self, cxn, context):
        i = 0
        self.program_and_run(sequence)
        
        while True:
            i += 1
            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.iteritems())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                self.program_and_run(sequence)
            else:
                self.pulser.start_number(7)
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()


    def program_and_run(self, sequence):
        self.program_pulser(sequence)
        self.pulser.start_number(7)
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TestPulseSequence(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
