from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class spin_echo(pulse_sequence):
    """
    This is a spin echo corrective pulse sequence
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_0'),
        ('Pi_times', 'qubit_minus'),
        ('Pi_times', 'qubit_plus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        #  select which zeeman level to prepare
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0
        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus
        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterrogation.detuning + center)
        pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    p.MicrowaveInterrogation.duration/2.0)

        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterrogation.duration/2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # Pi around Y
        self.addTTL('MicrowaveTTL',
                    self.start + p.MicrowaveInterrogation.duration/2.0 + 2 * pulse_delay,
                    p.MicrowaveInterrogation.duration)

        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterrogation.duration/2.0 + pulse_delay,
                    p.MicrowaveInterrogation.duration + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + 3.0 * p.MicrowaveInterrogation.duration/2.0 + 3 * pulse_delay,
                    p.MicrowaveInterrogation.duration/2.0)

        self.addDDS('Microwave_qubit',
                    self.start + 3.0 * p.MicrowaveInterrogation.duration/2.0 + 2 * pulse_delay,
                    p.MicrowaveInterrogation.duration/2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        self.end = self.start + 2.0 * p.MicrowaveInterrogation.duration + 3.0 * pulse_delay
