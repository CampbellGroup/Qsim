from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.TestSubSequence import test_sub_sequence

class test_sequence(pulse_sequence):

    required_subsequences = [test_sub_sequence]
    
    def sequence(self):
        self.addSequence(test_sub_sequence)
