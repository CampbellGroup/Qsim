from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class microwave_interrogation_clock(pulse_sequence):

    required_parameters = [
        ('MicrowaveInterrogation', 'duration'),
        ('MicrowaveInterrogation', 'detuning'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Transitions', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.qubit_0
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