from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
import numpy as np
from labrad.units import WithUnit as U


class spin_echo_sequence(pulse_sequence):
    """
    This is a BB1 corrective pulse sequence
    """

    required_parameters = [
        ('MicrowaveInterogation', 'duration'),
        ('MicrowaveInterogation', 'detuning'),
        ('MicrowaveInterogation', 'power'),
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

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)

        # rotation around X
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))

        # rotation around Y
        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterogation.duration/2.0,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(90.0, 'deg'))

        # rotation around X
        self.addDDS('Microwave_qubit',
                    self.start + 3.0*p.MicrowaveInterogation.duration/2.0,
                    p.MicrowaveInterogation.duration/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))

        self.end = self.start + 2.0*p.MicrowaveInterogation.duration
