from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from .sub_sequences.doppler_cooling import DopplerCooling
from .sub_sequences.quadrupole_interrogation import QuadrupoleInterrogation
from .sub_sequences.turn_off_all import TurnOffAll
from .sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from .sub_sequences.optical_pumping import OpticalPumping
from .sub_sequences.deshelving import Deshelving


class QuadrupolePoint(PulseSequence):
    required_subsequences = [TurnOffAll, DopplerCooling, QuadrupoleInterrogation,
                             Deshelving, OpticalPumping, MicrowaveInterrogation,
                             StandardStateDetection]

    required_parameters = [
    ]

    def sequence(self):
        self.add_sequence(TurnOffAll)
        self.add_sequence(DopplerCooling)
        self.add_sequence(OpticalPumping)
        self.add_sequence(MicrowaveInterrogation)
        self.add_sequence(QuadrupoleInterrogation)
        self.add_sequence(StandardStateDetection)
        self.add_sequence(Deshelving)
