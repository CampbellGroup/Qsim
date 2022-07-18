from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import DopplerCooling
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from sub_sequences.deshelving import Deshelving
from sub_sequences.shelving import Shelving
from sub_sequences.double_pass_369 import DoublePass369


class doppler_cooling_leakthrough_test(pulse_sequence):

    required_subsequences = [DopplerCooling, StandardStateDetection, OpticalPumping,
                             DopplerCooling, ShelvingStateDetection, Deshelving,
                             Shelving, ShelvingDopplerCooling, DoublePass369]

    required_parameters = [
        ('Modes', 'state_detection_mode'),
        ('EmptySequence', 'scan_empty_duration')
                           ]

    def sequence(self):
        p = self.parameters

        if p.Modes.state_detection_mode == 'Standard':
            self.addSequence(DopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(DoublePass369)
            self.addSequence(StandardStateDetection)

        elif p.Modes.state_detection_mode == 'Shelving':
            self.addSequence(ShelvingDopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(DoublePass369)
            self.addSequence(Shelving)
            self.addSequence(ShelvingStateDetection)
            self.addSequence(Deshelving)
