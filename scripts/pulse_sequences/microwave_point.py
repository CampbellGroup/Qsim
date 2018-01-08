from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.MicrowaveInterogation import microwave_interogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.StateDetection import state_detection
from sub_sequences.OpticalPumping import optical_pumping

class microwave_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling, microwave_interogation, state_detection, optical_pumping]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(microwave_interogation)
        self.addSequence(state_detection)