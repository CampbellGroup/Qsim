from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from scripts.pulse_sequences.sub_sequences.quadrupole_interrogation import (
    quadrupole_interogation,
)
from scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import (
    ShelvingStateDetection,
)
from scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import (
    ShelvingDopplerCooling,
)
from scripts.pulse_sequences.sub_sequences._deprecated.ZeemanOpticalPumping import (
    zeeman_bright_optical_pumping,
)
from scripts.pulse_sequences.sub_sequences._deprecated.ZeemanOpticalPumping import (
    zeeman_dark_optical_pumping,
)
from scripts.pulse_sequences.sub_sequences.shelving import Shelving
from scripts.pulse_sequences.sub_sequences.deshelving import Deshelving


class zeeman_fidelity(PulseSequence):

    required_subsequences = [
        TurnOffAll,
        quadrupole_interogation,
        ShelvingStateDetection,
        Shelving,
        ShelvingDopplerCooling,
        Deshelving,
        zeeman_bright_optical_pumping,
        zeeman_dark_optical_pumping,
    ]

    required_parameters = []

    def sequence(self):

        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingDopplerCooling)
        self.add_sequence(zeeman_bright_optical_pumping)
        self.add_sequence(Shelving)
        self.add_sequence(ShelvingStateDetection)
        self.add_sequence(Deshelving)

        self.add_sequence(ShelvingDopplerCooling)
        self.add_sequence(zeeman_dark_optical_pumping)
        self.add_sequence(Shelving)
        self.add_sequence(ShelvingStateDetection)
        self.add_sequence(Deshelving)
