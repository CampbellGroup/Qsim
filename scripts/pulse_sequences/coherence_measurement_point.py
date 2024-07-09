from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.doppler_cooling import DopplerCooling
from .sub_sequences.turn_off_all import TurnOffAll
from .sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from .sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from .sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from .sub_sequences.optical_pumping import OpticalPumping
from .sub_sequences.empty_sequence import EmptySequence
from .sub_sequences.shelving import Shelving
from .sub_sequences.deshelving import Deshelving
from .sub_sequences.coherence_measurement_microwave_sequence import CoherenceMeasurementMicrowaveSequence


class CoherenceMeasurementPoint(PulseSequence):

    required_subsequences = [TurnOffAll, DopplerCooling,
                             ShelvingStateDetection,
                             Deshelving, StandardStateDetection,
                             OpticalPumping, EmptySequence, Shelving,
                             CoherenceMeasurementMicrowaveSequence, ShelvingDopplerCooling]

    required_parameters = [
                          ('Modes', 'state_detection_mode')
        ]

    def sequence(self):
        mode = self.parameters.Modes.state_detection_mode

        if mode == 'Shelving':
            self.add_sequence(TurnOffAll)
            self.add_sequence(ShelvingDopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(CoherenceMeasurementMicrowaveSequence)
            self.add_sequence(Shelving)
            self.add_sequence(ShelvingStateDetection)
            self.add_sequence(Deshelving)
        elif mode == 'Standard':
            self.add_sequence(TurnOffAll)
            self.add_sequence(DopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(CoherenceMeasurementMicrowaveSequence)
            self.add_sequence(StandardStateDetection)
