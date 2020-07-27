from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class spin_echo_pi_pulse_clock(pulse_sequence):
    """
    This is a spin echo corrective pulse sequence
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'power'),
        ('Transitions', 'qubit_0'),
        ('Pi_times', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        #  select which zeeman level to prepare
        center = p.Transitions.qubit_0
        pi_time = p.Pi_times.qubit_0

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (center)
        pulse_delay = U(800.0, 'us')

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    pi_time / 2.0)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # Pi around Y
        self.addTTL('MicrowaveTTL',
                    self.start + pi_time / 2.0 + 2 * pulse_delay,
                    pi_time)

        self.addDDS('Microwave_qubit',
                    self.start + pi_time / 2.0 + pulse_delay,
                    pi_time + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + 3.0 * pi_time / 2.0 + 3 * pulse_delay,
                    pi_time / 2.0)

        self.addDDS('Microwave_qubit',
                    self.start + 3.0 * pi_time / 2.0 + 2 * pulse_delay,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        self.end = self.start + 2.0 * pi_time + 3.0 * pulse_delay


class spin_echo_pi_pulse_plus(pulse_sequence):
    """
    This is a spin echo corrective pulse sequence
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'power'),
        ('Transitions', 'qubit_plus'),
        ('Pi_times', 'qubit_plus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        #  select which zeeman level to prepare
        center = p.Transitions.qubit_plus
        pi_time = p.Pi_times.qubit_plus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (center)
        pulse_delay = U(10.0, 'us')

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    pi_time / 2.0)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # Pi around Y
        self.addTTL('MicrowaveTTL',
                    self.start + pi_time / 2.0 + 2 * pulse_delay,
                    pi_time)

        self.addDDS('Microwave_qubit',
                    self.start + pi_time / 2.0 + pulse_delay,
                    pi_time + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + 3.0 * pi_time / 2.0 + 3 * pulse_delay,
                    pi_time / 2.0)

        self.addDDS('Microwave_qubit',
                    self.start + 3.0 * pi_time / 2.0 + 2 * pulse_delay,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        self.end = self.start + 2.0 * pi_time + 3.0 * pulse_delay


class spin_echo_pi_pulse_minus(pulse_sequence):
    """
    This is a spin echo corrective pulse sequence
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'power'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        #  select which zeeman level to prepare
        center = p.Transitions.qubit_minus
        pi_time = p.Pi_times.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (center)
        pulse_delay = U(10.0, 'us')

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    pi_time / 2.0)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # Pi around Y
        self.addTTL('MicrowaveTTL',
                    self.start + pi_time / 2.0 + 2 * pulse_delay,
                    pi_time)

        self.addDDS('Microwave_qubit',
                    self.start + pi_time / 2.0 + pulse_delay,
                    pi_time + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # Pi/2 around X
        self.addTTL('MicrowaveTTL',
                    self.start + 3.0 * pi_time / 2.0 + 3 * pulse_delay,
                    pi_time / 2.0)

        self.addDDS('Microwave_qubit',
                    self.start + 3.0 * pi_time / 2.0 + 2 * pulse_delay,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        self.end = self.start + 2.0 * pi_time + 3.0 * pulse_delay