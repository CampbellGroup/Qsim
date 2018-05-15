from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.StateDetection import state_detection
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving
from sub_sequences.TurnOffAll import turn_off_all

class deshelving_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling, shelving, deshelving, state_detection]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(shelving)
        self.addSequence(deshelving)
        self.addSequence(state_detection)
