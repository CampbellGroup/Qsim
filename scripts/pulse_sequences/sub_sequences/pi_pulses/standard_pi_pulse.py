from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class standard_pi_pulse_clock(pulse_sequence):
    # this is a general microwave square pulse sequence where the different qubit lines
    # can be selected

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Transitions', 'qubit_0'),
        ('Pi_times', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        pi_time_0 = p.Pi_times.qubit_0

        DDS_0 = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_0
        ttl_delay = p.MicrowaveInterrogation.ttl_switch_delay

        self.addTTL('MicrowaveTTL',
                    self.start + ttl_delay,
                    pi_time_0)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time_0 + ttl_delay,
                    DDS_0,
                    p.MicrowaveInterrogation.power,
                    p.MicrowaveInterrogation.microwave_phase)

        self.end = self.start + pi_time_0 + ttl_delay


class standard_pi_pulse_plus(pulse_sequence):
    # this is a general microwave square pulse sequence where the different qubit lines
    # can be selected

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Transitions', 'qubit_plus'),
        ('Pi_times', 'qubit_plus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        pi_time_plus = p.Pi_times.qubit_plus

        DDS_plus = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_plus
        ttl_delay = p.MicrowaveInterrogation.ttl_switch_delay

        self.addTTL('MicrowaveTTL',
                    self.start + ttl_delay,
                    pi_time_plus)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time_plus + ttl_delay,
                    DDS_plus,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        self.end = self.start + pi_time_plus + ttl_delay


class standard_pi_pulse_minus(pulse_sequence):
    # this is a general microwave square pulse sequence where the different qubit lines
    # can be selected

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        pi_time_minus = p.Pi_times.qubit_minus

        DDS_minus = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_minus
        ttl_delay = p.MicrowaveInterrogation.ttl_switch_delay

        self.addTTL('MicrowaveTTL',
                    self.start + ttl_delay,
                    pi_time_minus)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time_minus + ttl_delay,
                    DDS_minus,
                    p.MicrowaveInterrogation.power,
                    p.MicrowaveInterrogation.microwave_phase)

        self.end = self.start + pi_time_minus + ttl_delay
