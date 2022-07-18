from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import doppler_cooling
from sub_sequences.dipole_interrogation import dipole_interrogation
from sub_sequences.turn_off_all import turn_off_all


class interleaved_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling, dipole_interrogation]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(dipole_interrogation)
