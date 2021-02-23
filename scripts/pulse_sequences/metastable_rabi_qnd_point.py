from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.MicrowaveInterrogation import microwave_interrogation
from sub_sequences.MetastableMicrowaveInterrogation import metastable_microwave_interrogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.MetastableStateDetection import metastable_state_detection
from sub_sequences.MetstableQNDDetection import metastable_qnd_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.HeraldedFourPreparation import heralded_four_preparation
from sub_sequences.MetastableRabiQND import metastable_rabi_qnd
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving


class metastable_rabi_qnd_point(pulse_sequence):

    required_subsequences = [turn_off_all, metastable_microwave_interrogation,
                             metastable_state_detection, optical_pumping, shelving,
                             shelving_doppler_cooling, deshelving, microwave_interrogation,
                             metastable_rabi_qnd, metastable_qnd_detection, heralded_four_preparation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)  # readout counts 1
        self.addSequence(optical_pumping)
        self.addSequence(microwave_interrogation)
        self.addSequence(shelving)
        self.addSequence(heralded_four_preparation)  # readout counts call 2
        self.addSequence(metastable_rabi_qnd)
        self.addSequence(metastable_qnd_detection)  # readout counts call 3
        self.addSequence(metastable_state_detection)  # readout counts call 4
        self.addSequence(deshelving)
