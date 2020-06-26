from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
import numpy as np
from labrad.units import WithUnit as U


class bb1(pulse_sequence):
    """
    This is a BB1 corrective pulse sequence
    """

    required_parameters = [
                           ('MicrowaveInterrogation', 'duration'),
                           ('MicrowaveInterrogation', 'detuning'),
                           ('MicrowaveInterrogation', 'power'),
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
            pi_time = p.Pi_times.qubit_0
            theta = (np.pi*p.MicrowaveInterrogation.duration/pi_time) % (4.0*np.pi)
        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus
            pi_time = p.Pi_times.qubit_plus
            theta = (np.pi*p.MicrowaveInterrogation.duration/pi_time) % (4.0*np.pi)
        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus
            pi_time = p.Pi_times.qubit_minus
            theta = (np.pi*p.MicrowaveInterrogation.duration/pi_time) % (4.0*np.pi)

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterrogation.detuning + center)
        phi1 = np.arccos(-theta/(4.0*np.pi))*180.0/np.pi
        phi2 = 3.0*phi1

        # initial attempt at rotation angle theta
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterrogation.duration,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        # corrective portion of the sequence
        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterrogation.duration,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phi1, 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + p.MicrowaveInterrogation.duration,
                    2.0*pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phi2, 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 3.0*pi_time + p.MicrowaveInterrogation.duration,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(phi1, 'deg'))

        self.end = self.start + 4.0*pi_time + p.MicrowaveInterrogation.duration
