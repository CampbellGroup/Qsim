from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class TestSubSequence(PulseSequence):
    required_parameters = []

    def sequence(self):
        p = self.parameters

        duration = U(500, 'us')

        self.add_ttl('ReadoutCount',
                     self.start,
                     duration)
        self.add_ttl('WindfreakSynthHDTTL',
                     self.start,
                     duration)
        self.add_ttl('TimeResolvedCount',
                     self.start,
                     duration)
        self.add_dds('760SP',
                     self.start,
                     duration,
                     U(160.0, "MHz"),
                     U(-10.0, "dBm"))

        self.end = self.start + duration

