from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.EmptySequence import empty_sequence
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.MicrowaveInterrogation import microwave_interrogation
from sub_sequences.MetastableRamseyMicrowaveInterrogation import metastable_ramsey_microwave_interrogation
from sub_sequences.MetastableStateDetection import metastable_state_detection
from sub_sequences.HeraldedFourPreparation import heralded_four_preparation


class heralded_metastable_microwave_ramsey_point(pulse_sequence):

    required_subsequences = [turn_off_all, deshelving, shelving_doppler_cooling,
                             optical_pumping, empty_sequence, shelving,
                             metastable_ramsey_microwave_interrogation, microwave_interrogation,
                             metastable_state_detection, heralded_four_preparation]

    required_parameters = [('MetastableMicrowaveRamsey', 'scan_type'),
                           ('MetastableMicrowaveRamsey', 'delay_time'),
                           ('MetastableMicrowaveRamsey', 'fixed_delay_time'),
                           ('MetastableMicrowaveRamsey', 'phase_scan'),
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)  # readout counts 1
        self.addSequence(optical_pumping)
        self.addSequence(microwave_interrogation)
        self.addSequence(shelving)
        self.addSequence(heralded_four_preparation)  # readout counts 2
        self.addSequence(metastable_ramsey_microwave_interrogation)
        self.addSequence(metastable_state_detection)  # readout counts 3
        self.addSequence(deshelving)

