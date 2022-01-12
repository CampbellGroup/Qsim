from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class microwave_sequence_standard(pulse_sequence):
    # this is a general microwave square pulse sequence where the different qubit lines
    # can be selected

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('MicrowaveInterrogation', 'microwave_source'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('Transitions', 'qubit_plus'),
        ('Transitions', 'qubit_minus'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('ddsDefaults', 'qubit_dds_x32_freq'),
        ('ddsDefaults', 'qubit_dds_x32_power')
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

        if p.MicrowaveInterrogation.microwave_source == 'HP+DDS':
            DDS_freq = p.ddsDefaults.qubit_dds_freq - (p.MicrowaveInterrogation.detuning + center)
            pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay

            self.addTTL('MicrowaveTTL',
                        self.start + pulse_delay,
                        p.MicrowaveInterrogation.duration)
            self.addDDS('Microwave_qubit',
                        self.start,
                        p.MicrowaveInterrogation.duration + pulse_delay,
                        DDS_freq,
                        p.MicrowaveInterrogation.power,
                        p.MicrowaveInterrogation.microwave_phase)

            self.end = self.start + p.MicrowaveInterrogation.duration + pulse_delay

        elif p.MicrowaveInterrogation.microwave_source == 'DDSx32':
            DDS_freq = p.ddsDefaults.qubit_dds_x32_freq + (p.MicrowaveInterrogation.detuning + center)/32.0
            pulse_delay = p.MicrowaveInterrogation.ttl_switch_delay

            self.addTTL('MicrowaveTTL',
                        self.start + pulse_delay,
                        p.MicrowaveInterrogation.duration)
            self.addDDS('Microwave_qubit',
                        self.start,
                        p.MicrowaveInterrogation.duration + pulse_delay,
                        DDS_freq,
                        p.ddsDefaults.qubit_dds_x32_power,
                        p.MicrowaveInterrogation.microwave_phase/32.0)

            self.end = self.start + p.MicrowaveInterrogation.duration + pulse_delay