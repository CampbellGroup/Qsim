from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class dipole_interogation(pulse_sequence):

    required_parameters = [
                           ('DipoleInterogation', 'duration'),
                           ('DipoleInterogation', 'frequency'),
                           ('DipoleInterogation', 'power')
                           ]

    def sequence(self):
        p = self.parameters
        self.addDDS('369',
                    self.start,
                    p.DipoleInterogation.duration,
                    p.DipoleInterogation.frequency,
                    p.DipoleInterogation.power)
        self.addTTL('TimeResolvedCount', self.start, p.interogation_time)
        self.end = self.start + p.interogation_time
