from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from scripts.pulse_sequences.sub_sequences.deshelving import Deshelving
from scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.BrightStatePumping import bright_state_pumping
from scripts.pulse_sequences.sub_sequences.shelving import Shelving


class manifold_measurement(pulse_sequence):

    required_subsequences = [ShelvingDopplerCooling, ShelvingStateDetection,
                             TurnOffAll, bright_state_pumping, Shelving, Deshelving]

    required_parameters = [
                           ('BrightStatePumping', 'bright_prep_method')
                           ]

    def sequence(self):
        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)

        self.addSequence(TurnOffAll)
        self.addSequence(bright_state_pumping)

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingStateDetection)

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)

        self.addSequence(TurnOffAll)
        self.addSequence(Shelving)

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingStateDetection)

        self.addSequence(TurnOffAll)
        self.addSequence(Deshelving)
