from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from sub_sequences.doppler_cooling import DopplerCooling
from sub_sequences.quadrupole_interrogation import QuadrupoleInterrogation
from sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.deshelving import Deshelving


class QuadrupolePoint(pulse_sequence):

    required_subsequences = [TurnOffAll, DopplerCooling, QuadrupoleInterrogation,
                             Deshelving, OpticalPumping, MicrowaveInterrogation,
                             StandardStateDetection]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(TurnOffAll)
        self.addSequence(DopplerCooling)
        self.addSequence(OpticalPumping)
        self.addSequence(MicrowaveInterrogation)
        self.addSequence(QuadrupoleInterrogation)
        self.addSequence(StandardStateDetection)
        self.addSequence(Deshelving)
