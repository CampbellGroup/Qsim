from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class hadamard(pulse_sequence):
    # this is a fixed pi/2 gate with arbitrary phase, although it is only a true hadamard when a specific phase
    # is chosen i believe

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_0'),
        ('Pi_times', 'qubit_plus'),
        ('Pi_times', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq')
                           ]

    def sequence(self):
        p = self.parameters

        #  select which zeeman level to prepare
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0
            pi_time = p.Pi_times.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus
            pi_time = p.Pi_times.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus
            pi_time = p.Pi_times.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterrogation.detuning + center)

        pulse_delay = U(800.0, 'us')

        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    pi_time/2.0)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time/2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    p.MicrowaveInterrogation.microwave_phase)

        self.end = self.start + pi_time/2.0 + pulse_delay
