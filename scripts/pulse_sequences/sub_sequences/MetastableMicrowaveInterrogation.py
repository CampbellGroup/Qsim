from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.MetastableMicrowaveSequenceStandard import metastable_microwave_sequence_standard
from Qsim.scripts.pulse_sequences.sub_sequences.MetastableMicrowaveKnillSequence import metastable_microwave_knill_sequence


class metastable_microwave_interrogation(pulse_sequence):

    required_parameters = [
        ('Metastable_Microwave_Interrogation', 'duration'),
        ('Metastable_Microwave_Interrogation', 'detuning'),
        ('Metastable_Microwave_Interrogation', 'power'),
        ('Metastable_Microwave_Interrogation', 'pulse_sequence'),
        ('Transitions', 'MetastableQubit'),
        ('ddsDefaults', 'metastable_qubit_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_dds_power'),
    ]

    required_subsequences = [metastable_microwave_sequence_standard,
                             metastable_microwave_knill_sequence]

    def sequence(self):
        p = self.parameters

        if p.Metastable_Microwave_Interrogation.pulse_sequence == 'Standard':
            self.addSequence(metastable_microwave_sequence_standard)

        if p.Metastable_Microwave_Interrogation.pulse_sequence == 'Knill':
            self.addSequence(metastable_microwave_knill_sequence)