from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class metastable_microwave_sequence_standard(pulse_sequence):

    required_parameters = [
        ('Metastable_Microwave_Interrogation', 'duration'),
        ('Metastable_Microwave_Interrogation', 'detuning'),
        ('Metastable_Microwave_Interrogation', 'power'),
        ('Transitions', 'MetastableQubit'),
        ('ddsDefaults', 'metastable_qubit_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_dds_power'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_1_power'),
    ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.MetastableQubit
        DDS_freq = p.ddsDefaults.metastable_qubit_dds_freq + (p.Metastable_Microwave_Interrogation.detuning + center)/8.0

        self.addDDS('3GHz_qubit',
                    self.start,
                    p.Metastable_Microwave_Interrogation.duration,
                    DDS_freq,
                    p.ddsDefaults.metastable_qubit_dds_power)

        self.end = self.start + p.Metastable_Microwave_Interrogation.duration
