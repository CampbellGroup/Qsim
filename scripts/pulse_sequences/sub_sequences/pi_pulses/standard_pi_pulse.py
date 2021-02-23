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
        ('Transitions', 'qubit_0'),
        ('Pi_times', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        center = p.Transitions.qubit_0
        pi_time = p.Pi_times.qubit_0

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (center)
        pulse_delay = U(2.0, 'us')

        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    pi_time)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    p.MicrowaveInterrogation.microwave_phase)

        self.end = self.start + pi_time + pulse_delay


class standard_pi_pulse_plus(pulse_sequence):
    # this is a general microwave square pulse sequence where the different qubit lines
    # can be selected

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('Transitions', 'qubit_plus'),
        ('Pi_times', 'qubit_plus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        center = p.Transitions.qubit_plus
        pi_time = p.Pi_times.qubit_plus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (center)
        pulse_delay = U(2.0, 'us')

        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    pi_time)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    p.MicrowaveInterrogation.microwave_phase)

        self.end = self.start + pi_time + pulse_delay


class standard_pi_pulse_minus(pulse_sequence):
    # this is a general microwave square pulse sequence where the different qubit lines
    # can be selected

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        center = p.Transitions.qubit_minus
        pi_time = p.Pi_times.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (center)
        pulse_delay = U(2.0, 'us')

        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    pi_time)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    p.MicrowaveInterrogation.microwave_phase)

        self.end = self.start + pi_time + pulse_delay
