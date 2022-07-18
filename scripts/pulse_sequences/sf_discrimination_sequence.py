from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.sf_discrimination_detection import SFDiscriminationDetection
from sub_sequences.turn_off_all import TurnOffAll


class sf_discrimination_sequence(pulse_sequence):

    required_subsequences = [TurnOffAll, SFDiscriminationDetection]

    required_parameters = [
        ]

    def sequence(self):
        p = self.parameters

        self.addSequence(TurnOffAll)
        self.addSequence(SFDiscriminationDetection)
