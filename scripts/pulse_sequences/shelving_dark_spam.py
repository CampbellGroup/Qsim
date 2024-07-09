from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from .sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from .sub_sequences.shelving import Shelving
from .sub_sequences.optical_pumping import OpticalPumping
from .sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from .sub_sequences.deshelving import Deshelving
from .sub_sequences.turn_off_all import TurnOffAll


class ShelvingDarkSpam(PulseSequence):
    required_subsequences = [Shelving, ShelvingDopplerCooling, ShelvingStateDetection, Deshelving,
                             OpticalPumping, MicrowaveInterrogation, TurnOffAll]

    required_parameters = [
    ]

    def sequence(self):
        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingDopplerCooling)
        self.add_sequence(OpticalPumping)
        self.add_sequence(MicrowaveInterrogation)
        self.add_sequence(Shelving)
        self.add_sequence(ShelvingStateDetection)
        self.add_sequence(Deshelving)
