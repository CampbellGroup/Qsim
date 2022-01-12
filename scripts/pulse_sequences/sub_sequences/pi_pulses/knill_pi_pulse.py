from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import numpy as np


class knill_pi_pulse_clock(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Pi_times', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq')
                           ]

    def sequence(self):
        p = self.parameters

        DDS_0 = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_0
        pi_time_0 = p.Pi_times.qubit_0

        ttl_delay = p.MicrowaveInterrogation.ttl_switch_delay

        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_delay,
                    pi_time_0)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time_0 + ttl_delay,
                    DDS_0,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        # pulse 2
        self.addTTL('MicrowaveTTL',
                    self.start + 2 * ttl_delay + pi_time_0,
                    pi_time_0)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time_0 + ttl_delay,
                    pi_time_0 + ttl_delay,
                    DDS_0,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 3 * ttl_delay + 2 * pi_time_0,
                    pi_time_0)
        self.addDDS('Microwave_qubit',
                    self.start + 2 * ttl_delay + 2 * pi_time_0,
                    pi_time_0 + ttl_delay,
                    DDS_0,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # pulse 4
        self.addTTL('MicrowaveTTL',
                    self.start + 4 * ttl_delay + 3 * pi_time_0,
                    pi_time_0)
        self.addDDS('Microwave_qubit',
                    self.start + 3 *ttl_delay + 3 * pi_time_0,
                    pi_time_0 + ttl_delay,
                    DDS_0,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 5
        self.addTTL('MicrowaveTTL',
                    self.start + 5 * ttl_delay + 4 * pi_time_0,
                    pi_time_0)
        self.addDDS('Microwave_qubit',
                    self.start + 4 * ttl_delay + 4 * pi_time_0,
                    pi_time_0 + ttl_delay,
                    DDS_0,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        self.end = self.start + 5 * pi_time_0 + 5 * ttl_delay


class knill_pi_pulse_plus(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Transitions', 'qubit_plus'),
        ('Pi_times', 'qubit_plus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        DDS_plus = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_plus
        pi_time_plus = p.Pi_times.qubit_plus
        ttl_delay = p.MicrowaveInterrogation.ttl_switch_delay

        print(p.Transitions.qubit_plus)

        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_delay,
                    pi_time_plus)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time_plus + ttl_delay,
                    DDS_plus,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        # pulse 2400.000000
        self.addTTL('MicrowaveTTL',
                    self.start + 2 * ttl_delay + pi_time_plus,
                    pi_time_plus)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time_plus + ttl_delay,
                    pi_time_plus + ttl_delay,
                    DDS_plus,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 3 * ttl_delay + 2 * pi_time_plus,
                    pi_time_plus)
        self.addDDS('Microwave_qubit',
                    self.start + 2 * ttl_delay + 2 * pi_time_plus,
                    pi_time_plus + ttl_delay,
                    DDS_plus,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # pulse 4
        self.addTTL('MicrowaveTTL',
                    self.start + 4 * ttl_delay + 3 * pi_time_plus,
                    pi_time_plus)
        self.addDDS('Microwave_qubit',
                    self.start + 3 * ttl_delay + 3 * pi_time_plus,
                    pi_time_plus + ttl_delay,
                    DDS_plus,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 5
        self.addTTL('MicrowaveTTL',
                    self.start + 5 * ttl_delay + 4 * pi_time_plus,
                    pi_time_plus)
        self.addDDS('Microwave_qubit',
                    self.start + 4 * ttl_delay + 4 * pi_time_plus,
                    pi_time_plus + ttl_delay,
                    DDS_plus,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        self.end = self.start + 5 * pi_time_plus + 5 * ttl_delay


class knill_pi_pulse_minus(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
    """


    required_parameters = [
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        DDS_minus = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_minus
        pi_time_minus = p.Pi_times.qubit_minus
        ttl_delay = p.MicrowaveInterrogation.ttl_switch_delay

        print(p.Transitions.qubit_minus)

        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_delay,
                    pi_time_minus)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time_minus + ttl_delay,
                    DDS_minus,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        # pulse 2
        self.addTTL('MicrowaveTTL',
                    self.start + 2 * ttl_delay + pi_time_minus,
                    pi_time_minus)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time_minus + ttl_delay,
                    pi_time_minus + ttl_delay,
                    DDS_minus,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 3 * ttl_delay + 2 * pi_time_minus,
                    pi_time_minus)
        self.addDDS('Microwave_qubit',
                    self.start + 2 * ttl_delay + 2 * pi_time_minus,
                    pi_time_minus + ttl_delay,
                    DDS_minus,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # pulse 4
        self.addTTL('MicrowaveTTL',
                    self.start + 4 * ttl_delay + 3 * pi_time_minus,
                    pi_time_minus)
        self.addDDS('Microwave_qubit',
                    self.start + 3 * ttl_delay + 3 * pi_time_minus,
                    pi_time_minus + ttl_delay,
                    DDS_minus,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # pulse 5
        self.addTTL('MicrowaveTTL',
                    self.start + 5 * ttl_delay + 4 * pi_time_minus,
                    pi_time_minus)
        self.addDDS('Microwave_qubit',
                    self.start + 4 * ttl_delay + 4 * pi_time_minus,
                    pi_time_minus + ttl_delay,
                    DDS_minus,
                    p.MicrowaveInterrogation.power,
                    U(30.0, 'deg'))

        self.end = self.start + 5 * pi_time_minus + 5 * ttl_delay
