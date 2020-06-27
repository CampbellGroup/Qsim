from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class knill_pi_pulse_clock(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'power'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Pi_times', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq')
                           ]

    def sequence(self):
        p = self.parameters
        
        center = p.Transitions.qubit_0
        pi_time = p.Pi_times.qubit_0
        
        DDS_freq = p.ddsDefaults.qubit_dds_freq -  center
        ttl_off = U(800.0, 'ns')
        ttl_delay = U(40.0, 'ns')
        start_delay = U(3.0, 'us')

        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + ttl_off + start_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        # pulse 2
        self.addTTL('MicrowaveTTL',
                    self.start + pi_time + 2 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + pi_time + 2 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 2 * pi_time + 3 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + 2 * pi_time + 3 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + 2 * pi_time + 2 * ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # pulse 4
        self.addTTL('MicrowaveTTL',
                    self.start + + 3 * pi_time + 4 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + + 3 * pi_time + 4 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + 3 * pi_time + 3 * ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 5
        self.addTTL('MicrowaveTTL',
                    self.start + + 4 * pi_time + 5 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + + 4 * pi_time + 5 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + 4 * pi_time + 4 * ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))


        self.end = self.start + 5 * pi_time + 5 * ttl_off + start_delay


class knill_pi_pulse_plus(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
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

        center = p.Transitions.qubit_plus
        pi_time = p.Pi_times.qubit_plus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - center
        ttl_off = U(800.0, 'ns')
        ttl_delay = U(40.0, 'ns')
        start_delay = U(3.0, 'us')

        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + ttl_off + start_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        # pulse 2
        self.addTTL('MicrowaveTTL',
                    self.start + pi_time + 2 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + pi_time + 2 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 2 * pi_time + 3 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + 2 * pi_time + 3 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + 2 * pi_time + 2 * ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # pulse 4
        self.addTTL('MicrowaveTTL',
                    self.start + + 3 * pi_time + 4 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + + 3 * pi_time + 4 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + 3 * pi_time + 3 * ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 5
        self.addTTL('MicrowaveTTL',
                    self.start + + 4 * pi_time + 5 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + + 4 * pi_time + 5 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + 4 * pi_time + 4 * ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        self.end = self.start + 5 * pi_time + 5 * ttl_off + start_delay


class knill_pi_pulse_minus(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
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

        center = p.Transitions.qubit_minus
        pi_time = p.Pi_times.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - center
        ttl_off = U(800.0, 'ns')
        ttl_delay = U(40.0, 'ns')
        start_delay = U(3.0, 'us')

        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + ttl_off + start_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        # pulse 2
        self.addTTL('MicrowaveTTL',
                    self.start + pi_time + 2 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + pi_time + 2 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 2 * pi_time + 3 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + 2 * pi_time + 3 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + 2 * pi_time + 2 * ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # pulse 4
        self.addTTL('MicrowaveTTL',
                    self.start + + 3 * pi_time + 4 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + + 3 * pi_time + 4 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + 3 * pi_time + 3 * ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 5
        self.addTTL('MicrowaveTTL',
                    self.start + + 4 * pi_time + 5 * ttl_off + start_delay,
                    pi_time - ttl_delay)
        self.addTTL('MicrowaveTTL3',
                    self.start + + 4 * pi_time + 5 * ttl_off + start_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + 4 * pi_time + 4 * ttl_off + start_delay,
                    pi_time + ttl_off,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        self.end = self.start + 5 * pi_time + 5 * ttl_off + start_delay
