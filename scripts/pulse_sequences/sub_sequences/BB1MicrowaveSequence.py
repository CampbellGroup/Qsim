from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
import numpy as np
from labrad.units import WithUnit as U


class bb1_sequence(pulse_sequence):
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
                           ]

    def sequence(self):
        p = self.parameters

        #  select which zeeman level to prepare
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0
            pi_time = p.Pi_times.qubit_0
            theta = (np.pi*p.MicrowaveInterogation.duration/pi_time) % (4*np.pi)
        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus
            pi_time = p.Pi_times.qubit_plus
            theta = (np.pi*p.MicrowaveInterogation.duration/pi_time) % (4*np.pi)
        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus
            pi_time = p.Pi_times.qubit_minus
            theta = (np.pi*p.MicrowaveInterogation.duration/pi_time) % (4*np.pi)

        DDS_freq = U(317.188, 'MHz') - (p.MicrowaveInterogation.detuning + center)
        phi1 = np.arccos(-theta/(4*np.pi))*180/np.pi
        phi2 = 3*phi1

        # initial attempt at rotation angle theta
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.MicrowaveInterogation.duration,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0, 'deg'))

        # corrective portion of the sequence
        self.addDDS('Microwave_qubit',
                    self.start + p.MicrowaveInterogation.duration,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(phi1, 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + p.MicrowaveInterogation.duration,
                    2*pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(phi2, 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 3*pi_time + p.MicrowaveInterogation.duration,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(phi1, 'deg'))
        self.end = self.start + 4*pi_time + p.MicrowaveInterogation.duration
