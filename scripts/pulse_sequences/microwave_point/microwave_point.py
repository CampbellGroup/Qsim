from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling import DopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import (
    MicrowaveInterrogation,
)
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import (
    StandardStateDetection,
)
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import (
    ShelvingStateDetection,
)
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import (
    ShelvingDopplerCooling,
)
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import Shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import Deshelving


class MicrowavePoint(PulseSequence):
    required_subsequences = [
        TurnOffAll,
        DopplerCooling,
        MicrowaveInterrogation,
        StandardStateDetection,
        ShelvingStateDetection,
        Deshelving,
        OpticalPumping,
        Shelving,
        ShelvingDopplerCooling,
    ]

    required_parameters = [
        ("Modes", "state_detection_mode"),
        ("MicrowaveInterrogation", "repetitions"),
    ]

    def sequence(self):
        p = self.parameters
        mode = p.Modes.state_detection_mode

        self.add_sequence(TurnOffAll)

        if mode == "Standard" or mode == "StandardFiberEOM":
            self.add_sequence(DopplerCooling)
            self.add_sequence(OpticalPumping)
            for i in range(int(p.MicrowaveInterrogation.repetitions)):
                self.add_sequence(MicrowaveInterrogation)
            self.add_sequence(StandardStateDetection)

        elif mode == "Shelving":
            self.add_sequence(ShelvingDopplerCooling)
            self.add_sequence(OpticalPumping)
            for i in range(int(p.MicrowaveInterrogation.repetitions)):
                self.add_sequence(MicrowaveInterrogation)
            self.add_sequence(Shelving)
            self.add_sequence(ShelvingStateDetection)
            self.add_sequence(Deshelving)
