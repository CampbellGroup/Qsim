from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.metastable_microwave_interrogation import MetastableMicrowaveInterrogation
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.metastable_state_detection import MetastableStateDetection
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import Shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import Deshelving
from Qsim.scripts.pulse_sequences.sub_sequences.heralded_four_preparation import HeraldedFourPreparation


class HeraldedMetastableMicrowavePoint(pulse_sequence):

    required_subsequences = [TurnOffAll, MetastableMicrowaveInterrogation,
                             MetastableStateDetection, OpticalPumping, Shelving,
                             ShelvingDopplerCooling, Deshelving, MicrowaveInterrogation,
                             HeraldedFourPreparation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)  # readout counts call 1
        # self.addSequence(optical_pumping)
        # self.addSequence(microwave_interrogation)
        self.addSequence(Shelving)
        self.addSequence(HeraldedFourPreparation)  # readout counts call 2
        self.addSequence(MetastableMicrowaveInterrogation)
        self.addSequence(MetastableStateDetection)  # readout counts call 3
        self.addSequence(Deshelving)
