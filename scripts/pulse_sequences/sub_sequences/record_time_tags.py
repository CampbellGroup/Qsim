from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class RecordTimeTags(pulse_sequence):

    required_parameters = [('RecordTimetags', 'record_timetags_duration')]

    def sequence(self):
        self.end = self.start + self.parameters.RecordTimetags.record_timetags_duration
        self.addTTL('TimeResolvedCount', self.start,
                    self.parameters.RecordTimetags.record_timetags_duration)
