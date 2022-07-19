from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import DopplerCooling
from sub_sequences.dipole_interrogation import DipoleInterrogation
from sub_sequences.turn_off_all import TurnOffAll


class InterleavedPoint(pulse_sequence):

    required_subsequences = [TurnOffAll, DopplerCooling, DipoleInterrogation]

    def sequence(self):
        self.addSequence(TurnOffAll)
        self.addSequence(DopplerCooling)
        self.addSequence(DipoleInterrogation)
