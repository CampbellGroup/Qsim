from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class microwave_interrogation_minus(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.qubit_minus
        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)
        pi_time = p.Pi_times.qubit_minus

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power)

        self.end = self.start + pi_time
