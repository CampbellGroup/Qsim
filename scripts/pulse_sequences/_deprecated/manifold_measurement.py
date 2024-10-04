from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import (
    ShelvingDopplerCooling,
)
from scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import (
    ShelvingStateDetection,
)
from scripts.pulse_sequences.sub_sequences.deshelving import Deshelving
from scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.BrightStatePumping import bright_state_pumping
from scripts.pulse_sequences.sub_sequences.shelving import Shelving


class manifold_measurement(PulseSequence):

    required_subsequences = [
        ShelvingDopplerCooling,
        ShelvingStateDetection,
        TurnOffAll,
        bright_state_pumping,
        Shelving,
        Deshelving,
    ]

    def sequence(self):
        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingDopplerCooling)

        self.add_sequence(TurnOffAll)
        self.add_sequence(bright_state_pumping)

        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingStateDetection)

        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingDopplerCooling)

        self.add_sequence(TurnOffAll)
        self.add_sequence(Shelving)

        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingStateDetection)

        self.add_sequence(TurnOffAll)
        self.add_sequence(Deshelving)
