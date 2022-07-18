from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import DopplerCooling
from sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.microwave_interrogation.ramsey_microwave_interrogation import RamseyMicrowaveInterrogation
from sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.shelving import Shelving
from sub_sequences.deshelving import Deshelving


class ramsey_microwave_line_scan_point(pulse_sequence):

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

        self.addSequence(TurnOffAll)

        if mode == 'Standard':
            self.addSequence(DopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(RamseyMicrowaveInterrogation)
            self.addSequence(StandardStateDetection)

        elif mode == 'Shelving':
            self.addSequence(ShelvingDopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(RamseyMicrowaveInterrogation)
            self.addSequence(Shelving)
            self.addSequence(ShelvingStateDetection)
            self.addSequence(Deshelving)
