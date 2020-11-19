from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class knill(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
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

        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterrogation.duration + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        # pulse 2
        self.addTTL('MicrowaveTTL',
                    self.start + 2*pulse_delay + p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterrogation.duration + pulse_delay,
                    p.MicrowaveInterrogation.duration + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 3*pulse_delay + 2*p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + 2*pulse_delay + 2*p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # pulse 4
        self.addTTL('MicrowaveTTL',
                    self.start + 4*pulse_delay + 3*p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + 3*pulse_delay + 3*p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 5
        self.addTTL('MicrowaveTTL',
                    self.start + 5*pulse_delay + 4*p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + 4*pulse_delay + 4*p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        self.end = self.start + 5 * p.MicrowaveInterrogation.duration + 5 * pulse_delay
