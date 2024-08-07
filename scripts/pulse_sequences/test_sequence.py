from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.test_sub_sequence import TestSubSequence
from .sub_sequences.turn_off_all import TurnOffAll
from .sub_sequences.optical_pumping import OpticalPumping
from .sub_sequences.doppler_cooling import DopplerCooling
from .sub_sequences.bright_state_pumping import BrightStatePumping
from .sub_sequences.dipole_interrogation import DipoleInterrogation


class TestSequence(PulseSequence):
    required_subsequences = [TestSubSequence,
                             TurnOffAll,
                             DopplerCooling,
                             BrightStatePumping,
                             OpticalPumping,
                             ]

    required_parameters = [
    ]

    def sequence(self):
        self.add_sequence(TestSubSequence)

