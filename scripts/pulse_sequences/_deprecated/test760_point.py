from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.EmptySequence import empty_sequence
from sub_sequences.Test760 import test760


class test_760_point(PulseSequence):

    required_subsequences = [empty_sequence, test760, turn_off_all]

    def sequence(self):
        self.add_sequence(turn_off_all)
        self.add_sequence(empty_sequence)
        self.add_sequence(test760)
