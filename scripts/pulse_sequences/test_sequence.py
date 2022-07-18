from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.test_sub_sequence import TestSubSequence


class test_sequence(pulse_sequence):

    required_subsequences = [TestSubSequence]

    def sequence(self):
        self.addSequence(TestSubSequence)
