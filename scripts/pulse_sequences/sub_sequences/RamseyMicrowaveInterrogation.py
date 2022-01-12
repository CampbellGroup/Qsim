from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class ramsey_microwave_interrogation(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('MicrowaveInterrogation', 'pulse_sequence'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('MicrowaveInterrogation', 'microwave_source'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('ddsDefaults', 'qubit_dds_x32_freq'),
        ('ddsDefaults', 'qubit_dds_x32_power'),
        ('ddsDefaults', 'DP2_411_freq'),
        ('ddsDefaults', 'DP2_411_power'),
        ('EmptySequence', 'duration'),
        ('Pi_times', 'qubit_0'),
        ('Pi_times', 'qubit_minus'),
        ('Pi_times', 'qubit_plus'),
                           ]

    def sequence(self):
        p = self.parameters

        #  select which mcirwave transition to drive
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0
            pi_time = p.Pi_times.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus
            pi_time = p.Pi_times.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus
            pi_time = p.Pi_times.qubit_minus

        if p.MicrowaveInterrogation.microwave_source == 'HP+DDS':
            DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterrogation.detuning + center)
            pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay

            # first pi/2 pulse, DDS turns on 800 us before the ttl allows it through
            self.addTTL('MicrowaveTTL',
                        self.start + pulse_delay,
                        pi_time/2.0)

            self.addDDS('Microwave_qubit',
                        self.start,
                        pi_time/2.0 + pulse_delay,
                        DDS_freq,
                        p.MicrowaveInterrogation.power,
                        U(0.0, 'deg'))

            # This 411 part is for the AC stark shift measurement to try to get the 411 beam waist...
            #
            # self.addDDS('411DP2',
            #             self.start + pi_time/2.0 + pulse_delay,
            #             p.EmptySequence.duration,
            #             p.ddsDefaults.DP2_411_freq,
            #             p.ddsDefaults.DP2_411_power,
            #             U(0.0, 'deg'))

            self.addTTL('MicrowaveTTL',
                        self.start + pi_time / 2.0 + p.EmptySequence.duration + pulse_delay,
                        pi_time / 2.0)

            self.addDDS('Microwave_qubit',
                        self.start + pi_time / 2.0 + p.EmptySequence.duration,
                        pi_time/2.0 + pulse_delay,
                        DDS_freq,
                        p.MicrowaveInterrogation.power,
                        p.MicrowaveInterrogation.microwave_phase)

            self.end = self.start + pi_time + p.EmptySequence.duration + pulse_delay

        elif p.MicrowaveInterrogation.microwave_source == 'DDSx32':
            DDS_freq = p.ddsDefaults.qubit_dds_x32_freq + (p.MicrowaveInterrogation.detuning + center)/32.0
            pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay

            self.addTTL('MicrowaveTTL',
                        self.start + pulse_delay,
                        pi_time / 2.0)
            self.addDDS('Microwave_qubit',
                        self.start,
                        pi_time / 2.0 + pulse_delay,
                        DDS_freq,
                        p.ddsDefaults.qubit_dds_x32_power,
                        U(0.0, 'deg')/32.0)

            self.addTTL('MicrowaveTTL',
                        self.start + pi_time / 2.0 + p.EmptySequence.duration,
                        pi_time / 2.0 + pulse_delay)
            self.addDDS('Microwave_qubit',
                        self.start + pi_time / 2.0 + p.EmptySequence.duration,
                        pi_time / 2.0 + pulse_delay,
                        DDS_freq,
                        p.ddsDefaults.qubit_dds_x32_power,
                        p.MicrowaveInterrogation.microwave_phase/32.0)

            self.end = self.start + pi_time + p.EmptySequence.duration + pulse_delay
