from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.TestSubSequence import test_sub_sequence
from sub_sequences.EmptySequence import empty_sequence

class test_sequence(pulse_sequence):

    required_subsequences = [test_sub_sequence, empty_sequence]
    
    def sequence(self):
        self.addSequence(empty_sequence)
        self.addSequence(test_sub_sequence)
        self.addSequence(empty_sequence)
