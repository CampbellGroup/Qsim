from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.SF_Discrimination_Detection import sf_discrimination_detection
from sub_sequences.TurnOffAll import turn_off_all


class sf_discrimination_sequence(pulse_sequence):

    required_subsequences = [turn_off_all, sf_discrimination_detection]

    required_parameters = [
        ]

    def sequence(self):
       p = self.parameters

       self.addSequence(turn_off_all)
       self.addSequence(sf_discrimination_detection)
