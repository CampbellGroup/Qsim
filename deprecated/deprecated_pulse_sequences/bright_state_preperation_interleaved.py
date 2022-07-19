from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from scripts.pulse_sequences.sub_sequences.doppler_cooling import DopplerCooling
from scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from deprecated.deprecated_sub_sequences.MLStateDetection import ml_state_detection
from scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from scripts.pulse_sequences.sub_sequences.bright_state_pumping import BrightStatePumping
from scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from scripts.pulse_sequences.sub_sequences.shelving import Shelving


class bright_state_preperation_interleaved(pulse_sequence):

    required_subsequences = [DopplerCooling, StandardStateDetection, ml_state_detection,
                             ShelvingStateDetection, TurnOffAll, BrightStatePumping,
                             ShelvingDopplerCooling, Shelving]
    required_parameters = [
        ('Modes', 'state_detection_mode'), ('BrightStateDetection', 'NumberInterleavedSequences')]

    def sequence(self):
        N = self.parameters.BrightStateDetection.NumberInterleavedSequences
        mode = self.parameters.Modes.state_detection_mode

        self.addSequence(TurnOffAll)
        if mode == 'Standard':
            self.addSequence(DopplerCooling)
        elif mode == 'Shelving':
            self.addSequence(ShelvingDopplerCooling)

        self.addSequence(TurnOffAll)
        self.addSequence(BrightStatePumping)

        self.addSequence(TurnOffAll)
        if mode == 'Standard':
            self.addSequence(StandardStateDetection)
        elif mode == 'Shelving':
            self.addSequence(Shelving)
            self.addSequence(ShelvingStateDetection)
