from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from sub_sequences.bright_state_pumping import BrightStatePumping
from sub_sequences.empty_sequence import EmptySequence
from sub_sequences.shelving import Shelving
from sub_sequences.deshelving import Deshelving
from sub_sequences.turn_off_all import TurnOffAll


class ShelvingPoint(pulse_sequence):

    required_subsequences = [TurnOffAll, ShelvingDopplerCooling, Shelving,
                             Deshelving, ShelvingStateDetection, EmptySequence, BrightStatePumping]

    def sequence(self):
        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)

        self.addSequence(TurnOffAll)
        self.addSequence(BrightStatePumping)

        self.addSequence(TurnOffAll)
        self.addSequence(Shelving)

        self.addSequence(TurnOffAll)
        self.addSequence(EmptySequence)

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingStateDetection)

        self.addSequence(TurnOffAll)
        self.addSequence(Deshelving)
