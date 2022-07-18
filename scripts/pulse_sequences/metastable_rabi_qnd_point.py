from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from sub_sequences.microwave_interrogation.metastable_microwave_interrogation import MetastableMicrowaveInterrogation
from sub_sequences.turn_off_all import TurnOffAll
from sub_sequences.state_detection.metastable_state_detection import MetastableStateDetection
from sub_sequences.metstable_qnd_detection import MetastableQNDDetection
from sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from sub_sequences.heralded_four_preparation import HeraldedFourPreparation
from sub_sequences.metastable_rabi_qnd import MetastableRabiQND
from sub_sequences.optical_pumping import OpticalPumping
from sub_sequences.shelving import Shelving
from sub_sequences.deshelving import Deshelving


class metastable_rabi_qnd_point(pulse_sequence):

    required_subsequences = [TurnOffAll, MetastableMicrowaveInterrogation,
                             MetastableStateDetection, OpticalPumping, Shelving,
                             ShelvingDopplerCooling, Deshelving, MicrowaveInterrogation,
                             MetastableRabiQND, MetastableQNDDetection, HeraldedFourPreparation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)  # readout counts 1
        self.addSequence(OpticalPumping)
        self.addSequence(MicrowaveInterrogation)
        self.addSequence(Shelving)
        self.addSequence(HeraldedFourPreparation)  # readout counts call 2
        self.addSequence(MetastableRabiQND)
        self.addSequence(MetastableQNDDetection)  # readout counts call 3
        self.addSequence(MetastableStateDetection)  # readout counts call 4
        self.addSequence(Deshelving)
