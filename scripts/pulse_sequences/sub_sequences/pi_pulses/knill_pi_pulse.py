from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import numpy as np


class knill_pi_pulse_clock(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'power'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Pi_times', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq')
                           ]

    def sequence(self):
        p = self.parameters

        DDS_freq = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_0
        pi_time = p.Pi_times.qubit_0
        phis = np.array([30.0, 0.0, 90.0, 0.0, 30.0])

        t_buffer = U(2.0, 'us')

        self.addTTL('MicrowaveTTL',
                    self.start + t_buffer + U(500.0, 'ns'),
                    5 * pi_time)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + t_buffer,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[0] , 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + pi_time + t_buffer,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[1] , 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 2 * pi_time + t_buffer,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[2] , 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 3 * pi_time + t_buffer,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[3] , 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 4 * pi_time + t_buffer,
                    pi_time + t_buffer,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[4] , 'deg'))

        self.end = self.start + 5 * pi_time + 2 * t_buffer



class knill_pi_pulse_plus(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'power'),
        ('Transitions', 'qubit_plus'),
        ('Pi_times', 'qubit_plus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        DDS_freq = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_plus
        pi_time = p.Pi_times.qubit_plus
        phis = np.array([30.0, 0.0, 90.0, 0.0, 30.0])

        t_buffer = U(2.0, 'us')

        self.addTTL('MicrowaveTTL',
                    self.start + t_buffer + U(500.0, 'ns'),
                    5 * pi_time)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + t_buffer,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[0], 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + pi_time + t_buffer,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[1], 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 2 * pi_time + t_buffer,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[2], 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 3 * pi_time + t_buffer,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[3], 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 4 * pi_time + t_buffer,
                    pi_time + t_buffer,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[4], 'deg'))

        self.end = self.start + 5 * pi_time + 2 * t_buffer


class knill_pi_pulse_minus(pulse_sequence):
    """
    This is a knill sequence with variable pulse area and detuning
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'power'),
        ('Transitions', 'qubit_minus'),
        ('Pi_times', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        DDS_freq = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_minus
        pi_time = p.Pi_times.qubit_minus
        phis = np.array([30.0, 0.0, 90.0, 0.0, 30.0])

        t_buffer = U(2.0, 'us')

        self.addTTL('MicrowaveTTL',
                    self.start + t_buffer + U(500.0, 'ns'),
                    5 * pi_time)

        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + t_buffer,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[0], 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + pi_time + t_buffer,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[1], 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 2 * pi_time + t_buffer,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[2], 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 3 * pi_time + t_buffer,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[3], 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 4 * pi_time + t_buffer,
                    pi_time + t_buffer,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[4], 'deg'))

        self.end = self.start + 5 * pi_time + 2 * t_buffer