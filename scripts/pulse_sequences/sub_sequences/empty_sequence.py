from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class EmptySequence(PulseSequence):
    required_parameters = [('EmptySequence', 'duration')]

    def sequence(self):
        self.add_ttl('MicrowaveTTL',
                     self.start,
                     U(100, "us"))
        self.end = self.start + self.parameters["EmptySequence.duration"]
