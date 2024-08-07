from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.doppler_cooling import DopplerCooling
from .sub_sequences.turn_off_all import TurnOffAll
from .sub_sequences.optical_pumping import OpticalPumping
from .sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from .sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from .sub_sequences.deshelving import Deshelving
from .sub_sequences.shelving import Shelving


class OpticalPumpingPoint(PulseSequence):
    required_subsequences = [DopplerCooling, StandardStateDetection, TurnOffAll,
                             OpticalPumping, DopplerCooling, ShelvingStateDetection,
                             Deshelving, Shelving]

    required_parameters = [
        ('Modes', 'optical_pumping_mode'),
        ('Modes', 'state_detection_mode')
    ]

    def sequence(self):
        p = self.parameters

        self.add_sequence(TurnOffAll)

        mode = p["Modes.optical_pumping_mode"]

        if mode == 'Standard' or mode == 'StandardFiberEOM':
            self.add_sequence(DopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(StandardStateDetection)

        elif mode == 'QuadrupoleOnly':
            if p["Modes.state_detection_mode"] == 'Shelving':
                self.add_sequence(DopplerCooling)
                self.add_sequence(OpticalPumping)
                self.add_sequence(Shelving)
                self.add_sequence(ShelvingStateDetection)
                self.add_sequence(Deshelving)
            if p["Modes.state_detection_mode"] == 'Standard':
                self.add_sequence(DopplerCooling)
                self.add_sequence(OpticalPumping)
                self.add_sequence(StandardStateDetection)
                self.add_sequence(Deshelving)
