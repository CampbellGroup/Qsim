from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class empty_sequence(pulse_sequence):

    required_parameters = [('EmptySequence', 'duration')]

    def sequence(self):
        self.end = self.start + self.parameters.EmptySequence.duration
