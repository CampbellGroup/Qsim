from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from EmptySequency import empty_sequence


class dipole_interogation(pulse_sequence):

    required_parameters = [
                           ('DipoleInterogation', 'interogation_time'),
                           ('DipoleInterogation', 'interogation_frequency'),
                           ('DipoleInterogation', 'interogation_power')
                           ]

    required_subsequences = [empty_sequence]

    replaced_parameters = {
                           empty_sequence: [('EmptySequence', 'empty_sequence_duration')]
                           }

    def sequence(self):
        p = self.parameters.DipoleInterogation
        self.addDDS('369',
                    self.start,
                    p.interogation_time,
                    p.interogation_frequency,
                    p.interogation_power)
        self.addTTL('ReadoutCount', self.start, p.interogation_time)
        self.end = self.start + p.interogation_time
