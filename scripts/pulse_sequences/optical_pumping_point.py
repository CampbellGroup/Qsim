from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import DopplerCooling
from sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.doppler_cooling_fiber_eom import DopplerCoolingFiberEom
from sub_sequences.state_detection.standard_state_detection_fiber_eom import StandardStateDetectionFiberEom
from sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from sub_sequences.deshelving import Deshelving
from sub_sequences.shelving import Shelving


class optical_pumping_point(pulse_sequence):

    required_subsequences = [DopplerCooling, StandardStateDetection, TurnOffAll
                             , OpticalPumping, DopplerCooling, ShelvingStateDetection,
                             Deshelving, Shelving, DopplerCoolingFiberEom,
                             StandardStateDetectionFiberEom]

    required_parameters = [
        ('OpticalPumping', 'method'),
        ('Modes', 'state_detection_mode')
                           ]

    def sequence(self):
        p = self.parameters

        self.addSequence(TurnOffAll)

        if p.OpticalPumping.method == 'Standard':
            self.addSequence(DopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(StandardStateDetection)

        elif p.OpticalPumping.method == "StandardFiberEOM":
            self.addSequence(DopplerCoolingFiberEom)
            self.addSequence(OpticalPumping)
            self.addSequence(StandardStateDetectionFiberEom)

        elif p.OpticalPumping.method == 'QuadrupoleOnly':
            if p.Modes.state_detection_mode == 'Shelving':
                self.addSequence(DopplerCooling)
                self.addSequence(OpticalPumping)
                self.addSequence(Shelving)
                self.addSequence(ShelvingStateDetection)
                self.addSequence(Deshelving)
            if p.Modes.state_detection_mode == 'Standard':
                self.addSequence(DopplerCooling)
                self.addSequence(OpticalPumping)
                self.addSequence(StandardStateDetection)
                self.addSequence(Deshelving)