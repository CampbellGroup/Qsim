from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.ML_interogation import ML_interogation


class ML_decoherence(pulse_sequence):

    required_subsequences = [doppler_cooling, standard_state_detection,
                             turn_off_all, bright_state_pumping, optical_pumping, ML_interogation]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(bright_state_pumping)
        self.addSequence(ML_interogation)
        self.addSequence(standard_state_detection)
        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(ML_interogation)
        self.addSequence(standard_state_detection)
