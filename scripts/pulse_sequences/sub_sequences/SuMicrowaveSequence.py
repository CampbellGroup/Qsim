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
        t_buffer = U(15.0, 'us')


        self.addTTL('MicrowaveTTL',
                    self.start + t_buffer + U(500.0, 'ns'),
                    5*p.MicrowaveInterrogation.duration)

        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterrogation.duration + t_buffer,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[0] + phi_0, 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterrogation.duration + t_buffer,
                    p.MicrowaveInterrogation.duration,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[1] + phi_0, 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 2*p.MicrowaveInterrogation.duration + t_buffer,
                    p.MicrowaveInterrogation.duration,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[2] + phi_0, 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 3*p.MicrowaveInterrogation.duration + t_buffer,
                    p.MicrowaveInterrogation.duration,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[3] + phi_0, 'deg'))

        self.addDDS('Microwave_qubit',
                    self.start + 4*p.MicrowaveInterrogation.duration + t_buffer,
                    p.MicrowaveInterrogation.duration + t_buffer,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phis[4] + phi_0, 'deg'))

        self.end = self.start + 5 * p.MicrowaveInterrogation.duration + 2 * t_buffer
