from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.DipoleInterogation import dipole_interogation
from sub_sequences.TurnOffAll import turn_off_all


class interleaved_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling, dipole_interogation]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(dipole_interogation)
