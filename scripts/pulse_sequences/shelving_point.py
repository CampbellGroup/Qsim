from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from .sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from .sub_sequences.bright_state_pumping import BrightStatePumping
from .sub_sequences.empty_sequence import EmptySequence
from .sub_sequences.shelving import Shelving
from .sub_sequences.deshelving import Deshelving
from .sub_sequences.turn_off_all import TurnOffAll


class ShelvingPoint(PulseSequence):
    required_subsequences = [TurnOffAll, ShelvingDopplerCooling, Shelving,
                             Deshelving, ShelvingStateDetection, EmptySequence, BrightStatePumping]

    def sequence(self):
        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingDopplerCooling)

        self.add_sequence(TurnOffAll)
        self.add_sequence(BrightStatePumping)

        self.add_sequence(TurnOffAll)
        self.add_sequence(Shelving)

        self.add_sequence(TurnOffAll)
        self.add_sequence(EmptySequence)

        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingStateDetection)

        self.add_sequence(TurnOffAll)
        self.add_sequence(Deshelving)
