from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.sf_discrimination_detection import sf_discrimination_detection
from sub_sequences.turn_off_all import turn_off_all


class sf_discrimination_sequence(pulse_sequence):

    required_subsequences = [turn_off_all, sf_discrimination_detection]

    required_parameters = [
        ]

    def sequence(self):
        p = self.parameters

        self.addSequence(turn_off_all)
        self.addSequence(sf_discrimination_detection)
