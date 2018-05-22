from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.EmptySequence import empty_sequence
from sub_sequences.Test760 import test760

class test_760_point(pulse_sequence):

    required_subsequences = [turn_off_all, empty_sequence, test760]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(empty_sequence)
        self.addSequence(test760)


