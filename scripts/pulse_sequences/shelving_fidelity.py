from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from sub_sequences.shelving import Shelving
from sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from sub_sequences.bright_state_pumping import BrightStatePumping
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.deshelving import Deshelving


class ShelvingFidelity(pulse_sequence):

    required_subsequences = [Shelving, ShelvingDopplerCooling, ShelvingStateDetection, Deshelving,
                             TurnOffAll, BrightStatePumping, OpticalPumping]

    required_parameters = [
                           ]

    def sequence(self):
        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)

        self.addSequence(TurnOffAll)
        self.addSequence(BrightStatePumping)

        self.addSequence(TurnOffAll)
        self.addSequence(Shelving)

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingStateDetection)

        self.addSequence(TurnOffAll)
        self.addSequence(Deshelving)

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)

        self.addSequence(TurnOffAll)
        self.addSequence(OpticalPumping)

        self.addSequence(TurnOffAll)
        self.addSequence(Shelving)

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingStateDetection)

        self.addSequence(TurnOffAll)
        self.addSequence(Deshelving)
