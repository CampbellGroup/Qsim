from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class RamseyMicrowaveInterrogation(pulse_sequence):

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
        ('ddsDefaults', 'SP_532_freq'),
        ('ddsDefaults', 'SP_532_power'),
        ('EmptySequence', 'duration'),
        ('Pi_times', 'qubit_0'),
        ('Pi_times', 'qubit_minus'),
        ('Pi_times', 'qubit_plus'),
                           ]

    def sequence(self):
        p = self.parameters

        #  select which microwave transition to drive
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0
            pi_time = p.Pi_times.qubit_0
        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus
            pi_time = p.Pi_times.qubit_plus
        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus
            pi_time = p.Pi_times.qubit_minus
        else:
            raise ValueError("Incorrect qubit selection")

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

            # Uncomment this part if you're trying to perform light shift measurements

            # self.addDDS('532SP',
            #             self.start + pi_time/2.0 + pulse_delay,
            #             p.EmptySequence.duration,
            #             p.ddsDefaults.SP_532_freq,
            #             p.ddsDefaults.SP_532_power,
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
