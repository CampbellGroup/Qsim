from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class single_sequence_rb_testing(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Transitions', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('Pi_times', 'qubit_0')
                           ]

    def sequence(self):
        p = self.parameters

        DDS_freq = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_0
        pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay
        pi_time = p.Pi_times.qubit_0


        # Pauli Identity
        #self.addTTL('MicrowaveTTL',
        #            self.start + pulse_delay,
        #            pi_time)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + pulse_delay,
                    DDS_freq,
                    U(-46.0, 'dBm'),
                    U(0.0, 'deg'))

        # Clifford y
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay + pi_time + pulse_delay,
                    pi_time / 2.0)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + pulse_delay,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))


        # Pauli minus y
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay,
                    pi_time + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(270.0, 'deg'))


        #Clifford y
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay + pi_time + pulse_delay,
                    pi_time / 2.0)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay + pi_time + pulse_delay,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # Pauli minus y
        # self.addTTL('MicrowaveTTL',
        #             self.start + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay  + pi_time / 2.0 + pulse_delay + pi_time + pulse_delay + pulse_delay,
        #             pi_time)
        # self.addDDS('Microwave_qubit',
        #             self.start + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay  + pi_time / 2.0 + pulse_delay + pi_time + pulse_delay,
        #             pi_time + pulse_delay,
        #             DDS_freq,
        #             p.MicrowaveInterrogation.power,
        #             U(270.0, 'deg'))
        #
        # self.end = self.start + (3 * pi_time) + (2 * (pi_time / 2.0)) + (pulse_delay * 5)

        # Pauli Identity
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay  + pi_time / 2.0 + pulse_delay + pi_time + pulse_delay,
                    pi_time + pulse_delay,
                    DDS_freq,
                    U(-46.0, 'dBm'),
                    U(0.0, 'deg'))

        self.end = self.start + (3 * pi_time) + (2 * (pi_time / 2.0)) + (pulse_delay * 5)

        '''
        # Clifford y
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay,
                    pi_time / 2.0)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        # Pauli minus y
        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay + pi_time / 2.0 + pulse_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time / 2.0 + pulse_delay,
                    pi_time + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(270.0, 'deg'))

        # Clifford y
        self.addTTL('MicrowaveTTL',
                    self.start + pi_time / 2.0 + pulse_delay + pulse_delay + pi_time + pulse_delay,
                    pi_time / 2.0)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time / 2.0 + pulse_delay + pi_time + pulse_delay,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        self.end = self.start + (1 * pi_time) + (2 * (pi_time / 2.0)) + (pulse_delay * 3)
        '''
        '''
        # self.addTTL('MicrowaveTTL',
        #            self.start + pulse_delay,
        #            pi_time)
        self.addDDS('Microwave_qubit',
                    self.start,
                    pi_time + pulse_delay,
                    DDS_freq,
                    U(-40.0, 'dBm'),
                    U(0.0, 'deg'))

        self.addTTL('MicrowaveTTL',
                    self.start + pi_time + pulse_delay + pulse_delay,
                    pi_time / 2.0)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + pulse_delay,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(90.0, 'deg'))

        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay,
                    pi_time)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay,
                    pi_time + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(270.0, 'deg'))

        self.addTTL('MicrowaveTTL',
                    self.start + pulse_delay + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay + pi_time + pulse_delay,
                    pi_time / 2.0)
        self.addDDS('Microwave_qubit',
                    self.start + pi_time + pulse_delay + pi_time / 2.0 + pulse_delay + pi_time + pulse_delay,
                    pi_time / 2.0 + pulse_delay,
                    DDS_freq,
                    p.MicrowaveInterrogation.power,
                    U(0.0, 'deg'))

        self.end = self.start + (2 * pi_time) + (2 * (pi_time / 2.0)) + (pulse_delay * 4)
        '''



