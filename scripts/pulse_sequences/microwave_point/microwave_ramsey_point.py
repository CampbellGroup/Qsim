from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling import DopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.empty_sequence import EmptySequence
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import Shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import Deshelving
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.ramsey_microwave_interrogation import \
    RamseyMicrowaveInterrogation


class MicrowaveRamseyPoint(PulseSequence):
    required_subsequences = [TurnOffAll, DopplerCooling,
                             ShelvingStateDetection,
                             Deshelving, StandardStateDetection,
                             OpticalPumping, EmptySequence, Shelving,
                             RamseyMicrowaveInterrogation, ShelvingDopplerCooling]

    required_parameters = [
        ('Modes', 'state_detection_mode')
    ]

    def sequence(self):
        mode = self.parameters.Modes.state_detection_mode

        if mode == 'Shelving':
            self.add_sequence(TurnOffAll)
            self.add_sequence(ShelvingDopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(RamseyMicrowaveInterrogation)
            self.add_sequence(Shelving)
            self.add_sequence(ShelvingStateDetection)
            self.add_sequence(Deshelving)
        elif mode == 'Standard' or mode == 'StandardFiberEOM':
            self.add_sequence(TurnOffAll)
            self.add_sequence(DopplerCooling)
            self.add_sequence(OpticalPumping)
            self.add_sequence(RamseyMicrowaveInterrogation)
            self.add_sequence(StandardStateDetection)
        else:
            raise Exception("Unknown operating mode '{}'".format(mode))
