from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.StateDetection import state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving
from sub_sequences.VariableDeshelving import variable_deshelving
from sub_sequences.TurnOffAll import turn_off_all

class deshelving_point(pulse_sequence):

    required_subsequences = [turn_off_all, shelving_doppler_cooling, shelving, deshelving, variable_deshelving, state_detection]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(shelving)
        self.addSequence(variable_deshelving) #scannable duration hacks since cant replace parameter for just one
        self.addSequence(state_detection)
        self.addSequence(deshelving)
