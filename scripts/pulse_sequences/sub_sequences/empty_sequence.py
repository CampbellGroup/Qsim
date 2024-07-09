from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence


class EmptySequence(PulseSequence):
    required_parameters = [('EmptySequence', 'duration')]

    def sequence(self):
        self.end = self.start + self.parameters.EmptySequence.duration
