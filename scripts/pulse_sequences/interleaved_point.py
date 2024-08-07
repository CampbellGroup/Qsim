from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.doppler_cooling import DopplerCooling
from .sub_sequences.dipole_interrogation import DipoleInterrogation
from .sub_sequences.turn_off_all import TurnOffAll
from .sub_sequences.empty_sequence import EmptySequence


class InterleavedPoint(PulseSequence):
    required_subsequences = [TurnOffAll, DopplerCooling, DipoleInterrogation, EmptySequence]

    def sequence(self):
        self.add_sequence(EmptySequence)
        self.add_sequence(TurnOffAll)
        self.add_sequence(DopplerCooling)
        self.add_sequence(DipoleInterrogation)
