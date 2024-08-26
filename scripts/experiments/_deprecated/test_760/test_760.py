import labrad
from Qsim.scripts.pulse_sequences.test760_point import test_760_point  as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U

class Test760(QsimExperiment):

    name = 'Test760'

    exp_parameters = []
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        for i in range(10):
            print i
            print self.p.items()
            should_break = self.update_progress(i/10.0)
            if should_break:
                break
            self.program_pulser(sequence)
            self.pulser.start_number(5)
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Test760(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
