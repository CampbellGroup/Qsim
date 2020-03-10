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
                           ('Pi_times', 'qubit_plus'),
                           ('ddsDefaults', 'qubit_dds_freq')
                           ]

    def sequence(self):
        p = self.parameters

        center_0 = p.Transitions.qubit_0
        center_plus = p.Transitions.qubit_plus

        pi_time_0 = p.Pi_times.qubit_0
        pi_time_plus = p.Pi_times.qubit_plus

        DDS_0 = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center_0)
        DDS_plus = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center_plus)

        if p.MicrowaveInterogation.pulse_sequence == 'standard':
            self.addDDS('Microwave_qubit',
                        self.start,
                        pi_time_0,
                        DDS_0,
                        p.MicrowaveInterogation.power)
            self.addDDS('Microwave_qubit',
                        self.start + pi_time_0,
                        pi_time_plus,
                        DDS_plus,
                        p.MicrowaveInterogation.power)
            self.end = self.start + pi_time_0 + pi_time_plus

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
                        pi_time_plus,
                        DDS_plus,
                        p.MicrowaveInterogation.power,
                        U(30.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 5*pi_time_0 + pi_time_plus,
                        pi_time_plus,
                        DDS_plus,
                        p.MicrowaveInterogation.power,
                        U(0.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 5*pi_time_0 + 2*pi_time_plus,
                        pi_time_plus,
                        DDS_plus,
                        p.MicrowaveInterogation.power,
                        U(90.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 5*pi_time_0 + 3*pi_time_plus,
                        pi_time_plus,
                        DDS_plus,
                        p.MicrowaveInterogation.power,
                        U(0.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 5*pi_time_0 + 4*pi_time_plus,
                        pi_time_plus,
                        DDS_plus,
                        p.MicrowaveInterogation.power,
                        U(30.0, 'deg'))

            self.end = self.start + 5*pi_time_0 + 5*pi_time_plus
