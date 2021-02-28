from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
import numpy as np
from sub_sequences.MicrowaveInterrogation import microwave_interrogation
from sub_sequences.MetastableMicrowaveInterrogation import metastable_microwave_interrogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.MetastableStateDetection import metastable_state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving
from sub_sequences.HeraldedFourPreparation import heralded_four_preparation
from sub_sequences.MetastableMeasurementDrivenGate_deltaTheta import metastable_measurement_driven_gate_deltaTheta


class metastable_measurement_driven_gate(pulse_sequence):

    required_subsequences = [
        turn_off_all,
        metastable_state_detection, 
        optical_pumping, 
        shelving,
        shelving_doppler_cooling, 
        deshelving,
        heralded_four_preparation,
        metastable_measurement_driven_gate_deltaTheta,
        shelving_state_detection
        ]

    required_parameters = [
        ('MetastableMeasurementDrivenGate', 'total_num_sub_pulses'),
        ('MetastableMeasurementDrivenGate', 'current_pulse_index'),
        ('Pi_times', 'metastable_qubit'),
        ('Metastable_Microwave_Interrogation', 'duration')
        ]

    def sequence(self):

        p = self.parameters

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)  # readout counts call 1
        self.addSequence(optical_pumping)
        self.addSequence(shelving)
        self.addSequence(heralded_four_preparation)  # readout counts call 2
        self.addSequence(metastable_measurement_driven_gate_deltaTheta)
        self.addSequence(shelving_state_detection)  # readout counts call 3
        self.addSequence(metastable_state_detection)  # readout counts call 4
        self.addSequence(deshelving)
