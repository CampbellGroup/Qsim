from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling import DopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import StandardStateDetection
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.empty_sequence import EmptySequence
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import Shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import Deshelving
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.ramsey_microwave_interrogation_532 import RamseyMicrowaveInterrogation_532


class MicrowaveRamseyPoint532(pulse_sequence):

    required_subsequences = [TurnOffAll, DopplerCooling,
                             ShelvingStateDetection,
                             Deshelving, StandardStateDetection,
                             OpticalPumping, EmptySequence, Shelving,
                             RamseyMicrowaveInterrogation_532, ShelvingDopplerCooling]

    required_parameters = [
                          ('Modes', 'state_detection_mode')
        ]

    def sequence(self):
        mode = self.parameters.Modes.state_detection_mode

        if mode == 'Shelving':
            self.addSequence(TurnOffAll)
            self.addSequence(ShelvingDopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(RamseyMicrowaveInterrogation_532)
            self.addSequence(Shelving)
            self.addSequence(ShelvingStateDetection)
            self.addSequence(Deshelving)
        elif mode == 'Standard' or mode == 'StandardFiberEOM':
            self.addSequence(TurnOffAll)
            self.addSequence(DopplerCooling)
            self.addSequence(OpticalPumping)
            self.addSequence(RamseyMicrowaveInterrogation_532)
            self.addSequence(StandardStateDetection)
        else:
            raise Exception("Unknown operating mode '{}'".format(mode))