from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class metastable_rabi_qnd(pulse_sequence):

    required_parameters = [
        ('MetastableMicrowaveInterrogation', 'duration'),
        ('MetastableMicrowaveInterrogation', 'detuning'),
        ('MetastableMicrowaveInterrogation', 'power'),
        ('MetastableRabiQND', 'time_to_project'),
        ('MetastableRabiQND', 'projection_time'),
        ('Transitions', 'MetastableQubit'),
        ('ddsDefaults', 'metastable_qubit_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_dds_power'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_1_power'),
        ('Pi_times', 'metastable_qubit')
    ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.MetastableQubit
        DDS_freq = p.ddsDefaults.metastable_qubit_dds_freq - (p.MetastableMicrowaveInterrogation.detuning + center)

        if p.MetastableMicrowaveInterrogation.duration < p.MetastableRabiQND.time_to_project:
            self.addDDS('3GHz_qubit',
                        self.start,
                        p.MetastableMicrowaveInterrogation.duration,
                        DDS_freq,
                        p.ddsDefaults.metastable_qubit_dds_power)

            self.end = self.start + p.MetastableMicrowaveInterrogation.duration

        elif p.MetastableMicrowaveInterrogation.duration >= p.MetastableRabiQND.time_to_project:

            self.addDDS('3GHz_qubit',
                        self.start,
                        p.MetastableRabiQND.time_to_project,
                        DDS_freq,
                        p.ddsDefaults.metastable_qubit_dds_power,
                        U(0.0, 'deg'))

            self.addDDS('3GHz_qubit',
                        self.start + p.MetastableRabiQND.time_to_project,
                        p.Pi_times.metastable_qubit/2.0,
                        DDS_freq,
                        p.ddsDefaults.metastable_qubit_dds_power,
                        U(180.0, 'deg'))

            self.addDDS('760SP',
                        self.start + p.MetastableRabiQND.time_to_project + p.Pi_times.metastable_qubit/2.0,
                        p.MetastableRabiQND.projection_time,
                        p.ddsDefaults.repump_760_1_freq,
                        p.ddsDefaults.repump_760_1_power)

            self.addDDS('3GHz_qubit',
                        self.start + p.MetastableRabiQND.time_to_project + p.Pi_times.metastable_qubit/2.0 + p.MetastableRabiQND.projection_time,
                        p.Pi_times.metastable_qubit/2.0,
                        DDS_freq,
                        p.ddsDefaults.metastable_qubit_dds_power,
                        U(0.0, 'deg'))

            self.addDDS('3GHz_qubit',
                        self.start + p.MetastableRabiQND.time_to_project + p.Pi_times.metastable_qubit + p.MetastableRabiQND.projection_time,
                        p.MetastableMicrowaveInterrogation.duration - p.MetastableRabiQND.time_to_project,
                        DDS_freq,
                        p.ddsDefaults.metastable_qubit_dds_power,
                        U(0.0, 'deg'))

            #self.addDDS('3GHz_qubit',
            #            self.start + p.MetastableMicrowaveInterrogation.duration + p.Pi_times.metastable_qubit + p.MetastableRabiQND.projection_time,
            #            p.Pi_times.metastable_qubit,
            #            DDS_freq,
            #            p.ddsDefaults.metastable_qubit_dds_power)

            self.end = self.start + p.MetastableMicrowaveInterrogation.duration + p.MetastableRabiQND.projection_time + p.Pi_times.metastable_qubit
