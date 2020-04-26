import labrad
from Qsim.scripts.pulse_sequences.interleaved_modelocked_interrogation import interleaved_modelocked_interrogation as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment


class TimeHarp_Interleaved(QsimExperiment):
    """
    """

    name = 'TimeHarp Interleaved'

    exp_parameters = []
    exp_parameters.append(('TimeHarp_Interleaved', 'cooling_time'))
    exp_parameters.append(('TimeHarp_Interleaved', 'interogation_time'))
    exp_parameters.append(('TimeHarp_Interleaved', 'iterations'))
    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('DopplerCooling', 'duration'))
    exp_parameters.remove(('ML_interogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.p['DopplerCooling.duration'] = self.p.TimeHarp_Interleaved.cooling_time
        self.p['ML_interogation.duration'] = self.p.TimeHarp_Interleaved.interogation_time
        self.program_pulser()

    def program_pulser(self):
        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(int(self.p.TimeHarp_Interleaved.iterations))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TimeHarp_Interleaved(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
