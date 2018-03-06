from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.StateDetection import state_detection
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.OpticalPumping import optical_pumping

class fidelity_tweak_up(pulse_sequence):

    required_subsequences = [doppler_cooling, state_detection, turn_off_all, bright_state_pumping, optical_pumping]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(bright_state_pumping)
        self.addSequence(state_detection)
        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(state_detection)
