from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
import numpy as np
from labrad.units import WithUnit as U


class metastable_measurement_driven_gate_deltaTheta(pulse_sequence):

    required_parameters = [
        ('MetastableMeasurementDrivenGate', 'total_num_sub_pulses'),
        ('MetastableMeasurementDrivenGate', 'measurement_duration'),
        ('Transitions', 'MetastableQubit'),
        ('Pi_times', 'metastable_qubit'),
        ('ddsDefaults', 'metastable_qubit_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_dds_power'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_1_power'),
        ('ddsDefaults', 'repump_760_2_freq'),
        ('ddsDefaults', 'repump_760_2_power'),
        ('ddsDefaults', 'repump_976_freq'),
        ('ddsDefaults', 'repump_976_power')
    ]

    required_subsequences = []

    def sequence(self):
        p = self.parameters

        DDS_freq = p.ddsDefaults.metastable_qubit_dds_freq + p.Transitions.MetastableQubit/8.0
        N = p.MetastableMeasurementDrivenGate.total_num_sub_pulses
        t_deshelve = p.MetastableMeasurementDrivenGate.measurement_duration
        delta_t = p.Pi_times.metastable_qubit / N

        self.addDDS('976SP',
                    self.start,
                    N*(N+1)*delta_t + N*t_deshelve,
                    p.ddsDefaults.repump_976_freq,
                    p.ddsDefaults.repump_976_power)

        for n in np.linspace(1, int(N), int(N)):
            self.addDDS('3GHz_qubit',
                        self.start + n*(n-1.)*delta_t + (n-1.)*t_deshelve,
                        n*delta_t,
                        DDS_freq,
                        p.ddsDefaults.metastable_qubit_dds_power,
                        U(0.0, 'deg'))

            self.addDDS('760SP',
                        self.start + n*delta_t + n*(n-1)*delta_t + (n-1)*t_deshelve,
                        t_deshelve,
                        p.ddsDefaults.repump_760_1_freq,
                        p.ddsDefaults.repump_760_1_power)

            self.addDDS('3GHz_qubit',
                        self.start + n*delta_t + n*(n-1.)*delta_t + n*t_deshelve,
                        n*delta_t,
                        DDS_freq,
                        p.ddsDefaults.metastable_qubit_dds_power,
                        U(22.5, 'deg'))

        self.end = self.start + N*(N+1)*delta_t + N*t_deshelve
