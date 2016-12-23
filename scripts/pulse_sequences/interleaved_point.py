from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.DipoleInterogation import dipole_interogation


class interleaved_point(pulse_sequence):

    required_subsequences = [doppler_cooling, dipole_interogation]

    def sequence(self):
        self.addSequence(doppler_cooling)
        self.addSequence(dipole_interogation)
