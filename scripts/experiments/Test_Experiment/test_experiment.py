import labrad
from Qsim.scripts.pulse_sequences.test_sequence import TestSequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np
from common.lib.servers.Pulser2.pulser_ok import Pulser
from twisted.internet.defer import inlineCallbacks


class TestExperiment(QsimExperiment):
    """
    Generic experiment (sublclassed from QsimExperiment) with its own sequence and sub-sequence that can be altered
    to test any particular sequence desired without affecting any other experiment
    """

    name = 'Test Experiment'

    exp_parameters = []
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('Modes', 'state_detection_mode'))

    exp_parameters.extend(TestSequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser: Pulser = cxn.pulser
        self.context = context

    def run(self, cxn, context):

        i = 0
        self.program_pulser(TestSequence)

        # self._program_pulser()
        # self.pulser.program_sequence()
        # self.pulser.start_number(100)

        while True:
            should_break = self.update_progress(np.random.rand())
            if should_break:
                break
            self.run_sequence()
            print(i)
            i += 1

    @inlineCallbacks
    def _program_pulser(self):
        start = U(5.0, 'us')
        duration = U(500.0, 'us')

        yield self.pulser.new_sequence()
        yield self.pulser.add_ttl_pulse("ReadoutCount", start, duration)
        yield self.pulser.add_dds_pulses(
            [('760SP', start, duration, U(160.0, "MHz"), U(-10.0, "dBm"),
              U(0.0, "deg"), U(0.0, "MHz"), U(0.0, "dB"))]
        )


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TestExperiment(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
