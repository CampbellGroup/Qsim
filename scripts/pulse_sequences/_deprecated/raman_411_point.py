from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from scripts.pulse_sequences.sub_sequences.doppler_cooling import DopplerCooling
from scripts.pulse_sequences.sub_sequences._deprecated.Raman411Interogation import (
    raman_411_interogation,
)
from scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import (
    StandardStateDetection,
)
from scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import (
    MicrowaveInterrogation,
)
from scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping


class raman_411_point(PulseSequence):

    required_subsequences = [
        TurnOffAll,
        DopplerCooling,
        raman_411_interogation,
        StandardStateDetection,
        OpticalPumping,
        MicrowaveInterrogation,
    ]

    required_parameters = []

    def sequence(self):

        self.add_sequence(TurnOffAll)
        self.add_sequence(DopplerCooling)
        self.add_sequence(OpticalPumping)
        self.add_sequence(MicrowaveInterrogation)
        self.add_sequence(raman_411_interogation)
        self.add_sequence(MicrowaveInterrogation)
        self.add_sequence(StandardStateDetection)
