from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling import DopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.microwave_interrogation_clock import (
    MicrowaveInterrogationClock,
)
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import (
    StandardStateDetection,
)
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping


class MicrowavePointClock(PulseSequence):
    required_subsequences = [
        TurnOffAll,
        DopplerCooling,
        MicrowaveInterrogationClock,
        StandardStateDetection,
        OpticalPumping,
    ]

    required_parameters = []

    def sequence(self):
        p = self.parameters

        self.add_sequence(TurnOffAll)
        self.add_sequence(DopplerCooling)
        self.add_sequence(OpticalPumping)
        self.add_sequence(MicrowaveInterrogationClock)
        self.add_sequence(StandardStateDetection)
