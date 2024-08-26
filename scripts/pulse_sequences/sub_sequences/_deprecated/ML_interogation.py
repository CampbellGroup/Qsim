from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class ML_interogation(PulseSequence):

    required_parameters = [
                           ('ML_interogation', 'duration'),
                           ('ML_interogation', 'frequency'),
                           ('ML_interogation', 'power'),
                           ('ML_interogation', 'repump_power')
                           ]

    def sequence(self):
        p = self.parameters

        self.add_dds('935SP',
                     self.start,
                     p.ML_interogation.duration,
                     U(320.0, 'MHz'),
                     p.ML_interogation.repump_power)

        self.add_ttl('TimeHarpPMT', self.start, p.ML_interogation.duration)
#        self.addDDS('ModeLockedSP',
#                    self.start,
#                    p.ML_interogation.duration,
#                    p.ML_interogation.frequency,
#                    p.ML_interogation.power)
        self.end = self.start + p.ML_interogation.duration
