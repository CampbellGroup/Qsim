from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class clifford_X(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Transitions', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('Pi_times', 'qubit_0')
                           ]

    def sequence(self):
        p = self.parameters

        DDS_freq = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_0
        pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay
        pi_time = p.Pi_times.qubit_0

        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    pi_time / 2.0)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        self.end = self.start + pi_time / 2.0 + pulse_delay
