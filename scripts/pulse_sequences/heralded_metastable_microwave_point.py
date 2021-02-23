from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.MicrowaveInterrogation import microwave_interrogation
from sub_sequences.MetastableMicrowaveInterrogation import metastable_microwave_interrogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.MetastableStateDetection import metastable_state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving
from sub_sequences.HeraldedFourPreparation import heralded_four_preparation


class heralded_metastable_microwave_point(pulse_sequence):

    required_subsequences = [turn_off_all, metastable_microwave_interrogation,
                             metastable_state_detection, optical_pumping, shelving,
                             shelving_doppler_cooling, deshelving, microwave_interrogation,
                             heralded_four_preparation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)  # readout counts call 1
        self.addSequence(optical_pumping)
        #self.addSequence(microwave_interrogation)
        self.addSequence(shelving)
        self.addSequence(heralded_four_preparation)  # readout counts call 2
        self.addSequence(metastable_microwave_interrogation)
        self.addSequence(metastable_state_detection)  # readout counts call 3
        self.addSequence(deshelving)
