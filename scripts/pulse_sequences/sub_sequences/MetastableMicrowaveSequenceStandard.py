from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class metastable_microwave_sequence_standard(pulse_sequence):

    required_parameters = [
        ('MetastableMicrowaveInterrogation', 'duration'),
        ('MetastableMicrowaveInterrogation', 'detuning'),
        ('MetastableMicrowaveInterrogation', 'power'),
        ('Transitions', 'MetastableQubit'),
        ('ddsDefaults', 'metastable_qubit_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_dds_power'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_1_power'),
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

        #self.addDDS('760SP',
        #            self.start,
        #            p.MetastableMicrowaveInterrogation.duration,
        #            p.ddsDefaults.repump_760_1_freq,
        #            p.ddsDefaults.repump_760_1_power)

        self.end = self.start + p.MetastableMicrowaveInterrogation.duration
