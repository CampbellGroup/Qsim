from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.empty_sequence import EmptySequence
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import Shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import Deshelving
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import (
    ShelvingDopplerCooling,
)
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import (
    MicrowaveInterrogation,
)
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.metastable_ramsey_microwave_interrogation import (
    MetastableRamseyMicrowaveInterrogation,
)
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.metastable_state_detection import (
    MetastableStateDetection,
)


class MetastableMicrowaveRamseyPoint(PulseSequence):
    required_subsequences = [
        TurnOffAll,
        Deshelving,
        ShelvingDopplerCooling,
        OpticalPumping,
        EmptySequence,
        Shelving,
        MetastableRamseyMicrowaveInterrogation,
        MicrowaveInterrogation,
        MetastableStateDetection,
    ]

    required_parameters = [
        ("MetastableMicrowaveRamsey", "scan_type"),
        ("MetastableMicrowaveRamsey", "delay_time"),
        ("MetastableMicrowaveRamsey", "fixed_delay_time"),
        ("MetastableMicrowaveRamsey", "phase_scan"),
    ]

    def sequence(self):
        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingDopplerCooling)
        self.add_sequence(OpticalPumping)
        self.add_sequence(MicrowaveInterrogation)
        self.add_sequence(Shelving)
        self.add_sequence(MetastableRamseyMicrowaveInterrogation)
        self.add_sequence(MetastableStateDetection)
        self.add_sequence(Deshelving)
