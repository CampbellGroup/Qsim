from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.sf_discrimination_detection import SFDiscriminationDetection
from .sub_sequences.turn_off_all import TurnOffAll


class SFDiscriminationSequence(PulseSequence):
    required_subsequences = [TurnOffAll, SFDiscriminationDetection]

    required_parameters = [
    ]

    def sequence(self):
        p = self.parameters

        self.add_sequence(TurnOffAll)
        self.add_sequence(SFDiscriminationDetection)
