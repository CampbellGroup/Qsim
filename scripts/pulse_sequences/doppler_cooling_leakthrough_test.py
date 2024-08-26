from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.doppler_cooling import DopplerCooling
from .sub_sequences.optical_pumping import OpticalPumping
from .sub_sequences.state_detection.standard_state_detection import (
    StandardStateDetection,
)
from .sub_sequences.state_detection.shelving_state_detection import (
    ShelvingStateDetection,
)
from .sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from .sub_sequences.deshelving import Deshelving
from .sub_sequences.shelving import Shelving
from .sub_sequences.double_pass_369 import DoublePass369


class DopplerCoolingLeakthroughTest(PulseSequence):
    required_subsequences = [
        DopplerCooling,
        StandardStateDetection,
        OpticalPumping,
        DopplerCooling,
        ShelvingStateDetection,
        Deshelving,
        Shelving,
        ShelvingDopplerCooling,
        DoublePass369,
    ]

    required_parameters = [
        ("Modes", "state_detection_mode"),
        ("EmptySequence", "scan_empty_duration"),
    ]

    def sequence(self):
        p = self.parameters

        if p.Modes.state_detection_mode == "Standard":
            self.add_sequence(DopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(DoublePass369)
            self.add_sequence(StandardStateDetection)

        elif p.Modes.state_detection_mode == "Shelving":
            self.add_sequence(ShelvingDopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(DoublePass369)
            self.add_sequence(Shelving)
            self.add_sequence(ShelvingStateDetection)
            self.add_sequence(Deshelving)
