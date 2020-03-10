from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class spin_echo_knill_sequence(pulse_sequence):

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
            pi_time = p.Pi_times.qubit_0
        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus
            pi_time = p.Pi_times.qubit_plus
        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus
            pi_time = p.Pi_times.qubit_minus

        DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterogation.detuning + center)
        phases = [30.0, 0.0, 90.0, 0.0, 30.0]

        # pi_pulse 1
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[0], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + pi_time/2.0,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(90.0 + phases[0], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 3*pi_time/2.0,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[0], 'deg'))

        # pi_pulse 2
        self.addDDS('Microwave_qubit',
                    self.start + 2*pi_time,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[1], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + pi_time/2.0 + 2*pi_time,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(90.0 + phases[1], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 3*pi_time/2.0 + 2*pi_time,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[1], 'deg'))

        # pi_pulse 3
        self.addDDS('Microwave_qubit',
                    self.start + 4*pi_time,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[2], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + pi_time/2.0 + 4*pi_time,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(90.0 + phases[2], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 3*pi_time/2.0 + 4*pi_time,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[2], 'deg'))

        # pi_pulse 4
        self.addDDS('Microwave_qubit',
                    self.start + 6*pi_time,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[3], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + pi_time/2.0 + 6*pi_time,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(90.0 + phases[3], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 3*pi_time/2.0 + 6*pi_time,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[3], 'deg'))

        # pi_pulse 5
        self.addDDS('Microwave_qubit',
                    self.start + 8*pi_time,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[4], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + pi_time/2.0 + 8*pi_time,
                    pi_time,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(90.0 + phases[4], 'deg'))
        self.addDDS('Microwave_qubit',
                    self.start + 3*pi_time/2.0 + 8*pi_time,
                    pi_time/2.0,
                    DDS_freq,
                    p.MicrowaveInterogation.power,
                    U(0.0 + phases[4], 'deg'))

        self.end = self.start + 10*pi_time
