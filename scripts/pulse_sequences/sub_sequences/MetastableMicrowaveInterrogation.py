from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class metastable_microwave_interrogation(pulse_sequence):

    required_parameters = [
        ('MetastableMicrowaveInterrogation', 'duration'),
        ('MetastableMicrowaveInterrogation', 'detuning'),
        ('MetastableMicrowaveInterrogation', 'power'),
        ('Transitions', 'MetastableQubit'),
        ('Transitions', 'qubit_plus'),
        ('ddsDefaults', 'metastable_qubit_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_dds_power'),
    ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.MetastableQubit
        DDS_freq = p.ddsDefaults.metastable_qubit_dds_freq - (p.MetastableMicrowaveInterrogation.detuning + center)

        self.addDDS('3GHz_qubit',
                    self.start,
                    p.MetastableMicrowaveInterrogation.duration,
                    DDS_freq,
                    p.ddsDefaults.metastable_qubit_dds_power)

        self.end = self.start + p.MetastableMicrowaveInterrogation.duration
