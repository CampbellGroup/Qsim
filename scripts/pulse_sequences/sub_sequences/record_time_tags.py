from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence


class RecordTimeTags(PulseSequence):

    required_parameters = [('RecordTimetags', 'record_timetags_duration')]

    def sequence(self):
        self.end = self.start + self.parameters.RecordTimetags.record_timetags_duration
        self.add_ttl('TimeResolvedCount', self.start,
                     self.parameters.RecordTimetags.record_timetags_duration)
