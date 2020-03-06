from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class ML_interogation(pulse_sequence):

    required_parameters = [
                           ('ML_interogation', 'duration'),
                           ('ML_interogation', 'frequency'),
                           ('ML_interogation', 'power'),
                           ('ML_interogation', 'repump_power')
                           ]

    def sequence(self):
        p = self.parameters

        self.addDDS('935SP',
                    self.start,
                    p.ML_interogation.duration,
                    U(320.0, 'MHz'),
                    p.ML_interogation.repump_power)

        self.addTTL('TimeHarpPMT', self.start, p.ML_interogation.duration)
#        self.addDDS('ModeLockedSP',
#                    self.start,
#                    p.ML_interogation.duration,
#                    p.ML_interogation.frequency,
#                    p.ML_interogation.power)
        self.end = self.start + p.ML_interogation.duration
