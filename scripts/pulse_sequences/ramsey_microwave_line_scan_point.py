from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.doppler_cooling import DopplerCooling
from .sub_sequences.turn_off_all import TurnOffAll
from .sub_sequences.microwave_interrogation.ramsey_microwave_interrogation import RamseyMicrowaveInterrogation
from .sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from .sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from .sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from .sub_sequences.optical_pumping import OpticalPumping
from .sub_sequences.shelving import Shelving
from .sub_sequences.deshelving import Deshelving


class RamseyMicrowaveLineScanPoint(PulseSequence):

    required_subsequences = [TurnOffAll, DopplerCooling,
                             RamseyMicrowaveInterrogation,
                             StandardStateDetection, ShelvingStateDetection, Deshelving,
                             OpticalPumping, Shelving, ShelvingDopplerCooling]

    required_parameters = [
        ('Modes', 'state_detection_mode'),
        ('MicrowaveInterrogation', 'repetitions')
        ]

    def sequence(self):
        p = self.parameters
        mode = p.Modes.state_detection_mode

        self.add_sequence(TurnOffAll)

        if mode == 'Standard':
            self.add_sequence(DopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(RamseyMicrowaveInterrogation)
            self.add_sequence(StandardStateDetection)

        elif mode == 'Shelving':
            self.add_sequence(ShelvingDopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(RamseyMicrowaveInterrogation)
            self.add_sequence(Shelving)
            self.add_sequence(ShelvingStateDetection)
            self.add_sequence(Deshelving)
