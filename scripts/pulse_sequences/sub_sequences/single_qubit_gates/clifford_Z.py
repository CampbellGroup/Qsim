from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class clifford_Z(pulse_sequence):
    required_parameters = [
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Pi_times', 'qubit_0')
    ]

    def sequence(self):
        p = self.parameters
        pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay
        pi_time = p.Pi_times.qubit_0

        self.end = self.start + pi_time / 2.0
