from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import DopplerCooling
from sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from sub_sequences.bright_state_pumping import BrightStatePumping


class FidelityTweakUp(pulse_sequence):
    required_subsequences = [DopplerCooling, StandardStateDetection, TurnOffAll,
                             BrightStatePumping, OpticalPumping]

    required_parameters = [
    ]

    def sequence(self):
        self.addSequence(TurnOffAll)
        self.addSequence(DopplerCooling)
        self.addSequence(BrightStatePumping)
        self.addSequence(StandardStateDetection)

        self.addSequence(TurnOffAll)
        self.addSequence(DopplerCooling)
        self.addSequence(OpticalPumping)
        self.addSequence(StandardStateDetection)
