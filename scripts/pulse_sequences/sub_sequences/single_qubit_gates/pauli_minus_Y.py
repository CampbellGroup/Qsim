from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_minus_Y import clifford_minus_Y
from labrad.units import WithUnit as U


class pauli_minus_Y(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('MicrowaveInterrogation', 'overall_phase'),
        ('MicrowaveInterrogation', 'microwave_source'),
        ('Transitions', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('ddsDefaults', 'qubit_dds_x32_freq'),
        ('ddsDefaults', 'qubit_dds_x32_power'),
        ('Pi_times', 'qubit_0')
    ]
    '''
    required_subsequences = [
        clifford_minus_Y
        ]
    def sequence(self):
        self.addSequence(clifford_minus_Y)
        self.addSequence(clifford_minus_Y)
    '''
    def sequence(self):
        p = self.parameters

        if p.MicrowaveInterrogation.microwave_source == 'HP+DDS':
            DDS_freq = p.ddsDefaults.qubit_dds_freq - p.Transitions.qubit_0
            pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay
            pi_time = p.Pi_times.qubit_0

            self.addTTL('MicrowaveTTL',
                        self.start + pulse_delay,
                        pi_time)
            self.addDDS('Microwave_qubit',
                        self.start,
                        pi_time + pulse_delay,
                        DDS_freq,
                        p.MicrowaveInterrogation.power,
                        U(270.0, 'deg') + p.MicrowaveInterrogation.overall_phase)
            self.end = self.start + pi_time + pulse_delay

        elif p.MicrowaveInterrogation.microwave_source == 'DDSx32':
            DDS_freq = p.ddsDefaults.qubit_dds_x32_freq + p.Transitions.qubit_0/32.0
            pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay
            pi_time = p.Pi_times.qubit_0
            phase = U(270.0, 'deg')/32.0 + p.MicrowaveInterrogation.overall_phase

            self.addTTL('MicrowaveTTL',
                        self.start + pulse_delay,
                        pi_time)
            self.addDDS('Microwave_qubit',
                        self.start,
                        pi_time + pulse_delay,
                        DDS_freq,
                        p.ddsDefaults.qubit_dds_x32_power,
                        phase)
            self.end = self.start + pi_time + pulse_delay

