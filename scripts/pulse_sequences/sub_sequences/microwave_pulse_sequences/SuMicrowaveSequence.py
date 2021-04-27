from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import numpy as np

class su_sequence(pulse_sequence):
    """
    """

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('MicrowaveInterrogation', 'microwave_phase'),
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
        phi_0 = p.MicrowaveInterrogation.microwave_phase['deg']
        theta = 104.5
        phis = np.array([-3 * theta, -theta, 0.0, theta, 3*theta]) % 360.0
        ttl_delay = p.MicrowaveInterrogation.ttl_switch_delay



        # pulse 1
        self.addTTL('MicrowaveTTL',
                    self.start + ttl_delay,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterrogation.duration + ttl_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[0] + phi_0, 'deg'))

        # pulse 2
        self.addTTL('MicrowaveTTL',
                    self.start + 2*ttl_delay + p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterrogation.duration + ttl_delay,
                    p.MicrowaveInterrogation.duration + ttl_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[1] + phi_0, 'deg'))

        # pulse 3
        self.addTTL('MicrowaveTTL',
                    self.start + 3 * ttl_delay + 2 * p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + 2*p.MicrowaveInterrogation.duration + 2*ttl_delay,
                    p.MicrowaveInterrogation.duration + ttl_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[2] + phi_0, 'deg'))

        # pulse 4
        self.addTTL('MicrowaveTTL',
                    self.start + 4 * ttl_delay + 3 * p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + 3*p.MicrowaveInterrogation.duration + 3*ttl_delay,
                    p.MicrowaveInterrogation.duration + ttl_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[3] + phi_0, 'deg'))

        # pulse 5
        self.addTTL('MicrowaveTTL',
                    self.start + 5 * ttl_delay + 4 * p.MicrowaveInterrogation.duration,
                    p.MicrowaveInterrogation.duration)
        self.addDDS('Microwave_qubit',
                    self.start + 4*p.MicrowaveInterrogation.duration + 4*ttl_delay,
                    p.MicrowaveInterrogation.duration + ttl_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[4] + phi_0, 'deg'))

        self.end = self.start + 5 * p.MicrowaveInterrogation.duration + 5 * ttl_delay
