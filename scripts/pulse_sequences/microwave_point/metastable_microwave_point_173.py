from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.metastable_microwave_interrogation_173 import \
    MetastableMicrowaveInterrogation173, SweptMetastableMicrowaveInterrogation173
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.metastable_state_detection_173 import MetastableStateDetection173
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import Shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import Deshelving


class MetastableMicrowavePoint173(pulse_sequence):

    required_subsequences = [TurnOffAll, MetastableMicrowaveInterrogation173,
                             MetastableStateDetection173, OpticalPumping, Shelving,
                             ShelvingDopplerCooling, Deshelving, MicrowaveInterrogation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)
        self.addSequence(Shelving)
        self.addSequence(MetastableMicrowaveInterrogation173)
        self.addSequence(MetastableStateDetection173)
        self.addSequence(Deshelving)


class SweptMetastableMicrowavePoint173(pulse_sequence):

    required_subsequences = [TurnOffAll, SweptMetastableMicrowaveInterrogation173,
                             MetastableStateDetection173, OpticalPumping, Shelving,
                             ShelvingDopplerCooling, Deshelving, MicrowaveInterrogation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)
        self.addSequence(Shelving)
        self.addSequence(SweptMetastableMicrowaveInterrogation173)
        self.addSequence(MetastableStateDetection173)
        self.addSequence(Deshelving)
