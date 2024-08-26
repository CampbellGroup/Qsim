from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.MLStateDetection import ml_state_detection
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.BrightStatePumping import bright_state_pumping


class ML_interrogation_point(PulseSequence):

    required_subsequences = [doppler_cooling, turn_off_all, ml_state_detection, optical_pumping, bright_state_pumping]

    required_parameters = [('Delaystagescan', 'state_prep')]

    def sequence(self):
        self.add_sequence(turn_off_all)
        self.add_sequence(doppler_cooling)
        if self.parameters.Delaystagescan.state_prep == 'Dark':
            self.add_sequence(optical_pumping)
        elif self.parameters.Delaystagescan.state_prep == 'Bright':
            self.add_sequence(bright_state_pumping)
        self.add_sequence(ml_state_detection)
