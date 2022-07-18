from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from sub_sequences.shelving import shelving
from sub_sequences.deshelving import deshelving
from sub_sequences.variable_deshelving import variable_deshelving
from sub_sequences.turn_off_all import turn_off_all


class deshelving_point(pulse_sequence):

    required_subsequences = [turn_off_all, shelving_doppler_cooling, shelving,
                             deshelving, variable_deshelving, shelving_state_detection]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(shelving)
        self.addSequence(variable_deshelving)  # scannable duration hacks since cant replace parameter for just one
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving)
