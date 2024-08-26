from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence

from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.metastable_state_detection import (
    MetastableStateDetection,
)
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import (
    ShelvingDopplerCooling,
)
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import (
    ShelvingStateDetection,
)
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import Shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import Deshelving
from Qsim.scripts.pulse_sequences.sub_sequences.heralded_four_preparation import (
    HeraldedFourPreparation,
)
from Qsim.scripts.pulse_sequences.sub_sequences.metastable_measurement_driven_rabi import (
    MetastableMeasurementDrivenRabi,
)


class MetastableMeasurementDrivenRabiPoint(PulseSequence):
    required_subsequences = [
        TurnOffAll,
        MetastableStateDetection,
        OpticalPumping,
        Shelving,
        ShelvingDopplerCooling,
        Deshelving,
        HeraldedFourPreparation,
        MetastableMeasurementDrivenRabi,
        ShelvingStateDetection,
    ]

    required_parameters = [
        ("MetastableMeasurementDrivenGate", "total_num_sub_pulses"),
        ("MetastableMeasurementDrivenGate", "current_pulse_index"),
        ("Pi_times", "metastable_qubit"),
        ("Metastable_Microwave_Interrogation", "duration"),
    ]

    def sequence(self):
        p = self.parameters

        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingDopplerCooling)  # readout counts call 1
        self.add_sequence(OpticalPumping)
        self.add_sequence(Shelving)
        self.add_sequence(HeraldedFourPreparation)  # readout counts call 2
        self.add_sequence(MetastableMeasurementDrivenRabi)
        self.add_sequence(ShelvingStateDetection)  # readout counts call 3
        self.add_sequence(MetastableStateDetection)  # readout counts call 4
        self.add_sequence(Deshelving)
