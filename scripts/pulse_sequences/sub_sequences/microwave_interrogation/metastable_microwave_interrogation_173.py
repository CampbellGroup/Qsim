from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class MetastableMicrowaveInterrogation173(PulseSequence):

    required_parameters = [
        ('Metastable_Microwave_Interrogation', 'duration'),
        ('Metastable_Microwave_Interrogation', 'detuning'),
        ('Metastable_Microwave_Interrogation', 'power'),
        ('Metastable_Microwave_Interrogation', 'pulse_sequence'),
        ('Transitions', 'MetastableQubit173'),
        ('ddsDefaults', 'metastable_qubit_173_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_173_dds_power'),
    ]

    required_subsequences = []

    def sequence(self):
        p = self.parameters
        center = p.Transitions.MetastableQubit173
        DDS_freq = p.ddsDefaults.metastable_qubit_173_dds_freq + (
                    p.Metastable_Microwave_Interrogation.detuning + center) / 8.0

        self.add_dds('3GHz_qubit',
                     self.start,
                     p.Metastable_Microwave_Interrogation.duration,
                     DDS_freq,
                     p.ddsDefaults.metastable_qubit_173_dds_power)
        self.add_ttl('WindfreakSynthHDTTL',
                     self.start,
                     p.Metastable_Microwave_Interrogation.duration)
        self.add_ttl('WindfreakSynthNVTTL',
                     self.start,
                     p.Metastable_Microwave_Interrogation.duration)
        self.end = self.start + p.Metastable_Microwave_Interrogation.duration


class SweptMetastableMicrowaveInterrogation173(PulseSequence):

    required_parameters = [
        ('Metastable_Microwave_Interrogation', 'duration'),
        ('Metastable_Microwave_Interrogation', 'detuning'),
        ('Metastable_Microwave_Interrogation', 'power'),
        ('Metastable_Microwave_Interrogation', 'pulse_sequence'),
        ('Metastable_Microwave_Interrogation', 'ramp_width'),
        ('Transitions', 'MetastableQubit173'),
        ('ddsDefaults', 'metastable_qubit_173_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_173_dds_power'),
    ]

    required_subsequences = []

    def sequence(self):
        p = self.parameters
        center = p.Transitions.MetastableQubit173
        DDS_freq = p.ddsDefaults.metastable_qubit_173_dds_freq + (
                    p.Metastable_Microwave_Interrogation.detuning + center) / 8.0
        ramp_rate = U(p.Metastable_Microwave_Interrogation.ramp_width['MHz'] / p.Metastable_Microwave_Interrogation.duration['ms'], 'MHz')

        self.add_dds('3GHz_qubit',
                     self.start,
                     p.Metastable_Microwave_Interrogation.duration,
                     DDS_freq,
                     p.ddsDefaults.metastable_qubit_173_dds_power,
                     U(0.0, 'deg'),
                     ramp_rate)
        self.add_ttl('WindfreakSynthHDTTL',
                     self.start,
                     p.Metastable_Microwave_Interrogation.duration)
        self.add_ttl('WindfreakSynthNVTTL',
                     self.start,
                     p.Metastable_Microwave_Interrogation.duration)
        self.end = self.start + p.Metastable_Microwave_Interrogation.duration
