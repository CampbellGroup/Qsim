from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class double_microwave_sequence(pulse_sequence):

    required_parameters = [
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('MicrowaveInterogation', 'power'),
                           ('MicrowaveInterogation', 'pulse_sequence'),
                           ('Line_Selection', 'qubit'),
                           ('Transitions', 'qubit_0'),
                           ('Transitions', 'qubit_plus'),
                           ('Transitions', 'qubit_minus'),
                           ('Pi_times', 'qubit_0'),
                           ('Pi_times', 'qubit_minus'),
                           ]

    def sequence(self):
        p = self.parameters

        center_0 = p.Transitions.qubit_0
        center_minus = p.Transitions.qubit_minus

        pi_time_0 = p.Pi_times.qubit_0
        pi_time_minus = p.Pi_times.qubit_minus

        DDS_0 = U(317.188, 'MHz') - (p.MicrowaveInterogation.detuning + center_0)
        DDS_minus = U(317.188, 'MHz') - (p.MicrowaveInterogation.detuning + center_minus)

        if p.MicrowaveInterogation.pulse_sequence == 'standard':
            self.addDDS('Microwave_qubit',
                        self.start,
                        pi_time_0,
                        DDS_0,
                        p.MicrowaveInterogation.power)
            self.addDDS('Microwave_qubit',
                        self.start + pi_time_0,
                        pi_time_minus,
                        DDS_minus,
                        p.MicrowaveInterogation.power)
            self.end = self.start + pi_time_0 + pi_time_minus

        elif p.MicrowaveInterogation.pulse_sequence == 'knill':
            self.addDDS('Microwave_qubit',
                        self.start,
                        pi_time_0,
                        DDS_0,
                        p.MicrowaveInterogation.power,
                        U(30.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + pi_time_0,
                        pi_time_0,
                        DDS_0,
                        p.MicrowaveInterogation.power,
                        U(0.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 2*pi_time_0,
                        pi_time_0,
                        DDS_0,
                        p.MicrowaveInterogation.power,
                        U(90.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 3*pi_time_0,
                        pi_time_0,
                        DDS_0,
                        p.MicrowaveInterogation.power,
                        U(0.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 4*pi_time_0,
                        pi_time_0,
                        DDS_0,
                        p.MicrowaveInterogation.power,
                        U(30.0, 'deg'))

            self.addDDS('Microwave_qubit',
                        self.start + 5*pi_time_0,
                        pi_time_minus,
                        DDS_minus,
                        p.MicrowaveInterogation.power,
                        U(30.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 5*pi_time_0 + pi_time_minus,
                        pi_time_minus,
                        DDS_minus,
                        p.MicrowaveInterogation.power,
                        U(0.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 5*pi_time_0 + 2*pi_time_minus,
                        pi_time_minus,
                        DDS_minus,
                        p.MicrowaveInterogation.power,
                        U(90.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 5*pi_time_0 + 3*pi_time_minus,
                        pi_time_minus,
                        DDS_minus,
                        p.MicrowaveInterogation.power,
                        U(0.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 5*pi_time_0 + 4*pi_time_minus,
                        pi_time_minus,
                        DDS_minus,
                        p.MicrowaveInterogation.power,
                        U(30.0, 'deg'))

            self.end = self.start + 5*pi_time_0 + 5*pi_time_minus
