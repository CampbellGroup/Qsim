from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.StateDetection import state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.EmptySequence import empty_sequence
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving
from sub_sequences.TurnOffAll import turn_off_all

class shelving_point(pulse_sequence):

    required_subsequences = [turn_off_all, shelving_doppler_cooling, shelving, deshelving, state_detection, empty_sequence]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(shelving)
        self.addSequence(empty_sequence)
        self.addSequence(state_detection)
        self.addSequence(deshelving)
