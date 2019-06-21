from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.MLStateDetection import ml_state_detection
from sub_sequences.TurnOffAll import turn_off_all


class ML_interrogation_point(pulse_sequence):

    required_subsequences = [doppler_cooling, turn_off_all, ml_state_detection]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(ml_state_detection)
