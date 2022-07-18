from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import turn_off_all
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import optical_pumping
from Qsim.scripts.pulse_sequences.sub_sequences.empty_sequence import empty_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import deshelving
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interrogation
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.metastable_ramsey_microwave_interrogation import metastable_ramsey_microwave_interrogation
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.metastable_state_detection import metastable_state_detection
from Qsim.scripts.pulse_sequences.sub_sequences.heralded_four_preparation import heralded_four_preparation


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
