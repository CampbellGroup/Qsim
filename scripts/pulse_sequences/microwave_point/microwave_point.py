from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling import DopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling_fiber_eom import DopplerCoolingFiberEom
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection_fiber_eom import StandardStateDetectionFiberEom
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import Shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import Deshelving


class MicrowavePoint(pulse_sequence):

    required_subsequences = [TurnOffAll, DopplerCooling,
                             MicrowaveInterrogation,
                             StandardStateDetection, ShelvingStateDetection, Deshelving,
                             OpticalPumping, Shelving, ShelvingDopplerCooling, DopplerCoolingFiberEom,
                             StandardStateDetectionFiberEom]

    required_parameters = [
        ('Modes', 'state_detection_mode'),
        ('MicrowaveInterrogation', 'repetitions')
        ]

    def sequence(self):
        p = self.parameters
        mode = p.Modes.state_detection_mode

        self.addSequence(TurnOffAll)

        if mode == 'Standard' or mode == 'StandardFiberEOM':
            self.addSequence(DopplerCooling)
            self.addSequence(OpticalPumping)
            for i in range(int(p.MicrowaveInterrogation.repetitions)):
                self.addSequence(MicrowaveInterrogation)
            self.addSequence(StandardStateDetection)

        elif mode == 'Shelving':
            self.addSequence(ShelvingDopplerCooling)
            self.addSequence(OpticalPumping)
            for i in range(int(p.MicrowaveInterrogation.repetitions)):
                self.addSequence(MicrowaveInterrogation)
            self.addSequence(Shelving)
            self.addSequence(ShelvingStateDetection)
            self.addSequence(Deshelving)
