from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.StateDetection import state_detection
from sub_sequences.TurnOffAll import turn_off_all

class dark_state_preperation(pulse_sequence):

    required_subsequences = [doppler_cooling, optical_pumping, state_detection, turn_off_all]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(state_detection)