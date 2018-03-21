from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class dipole_interogation(pulse_sequence):

    required_parameters = [
                           ('DipoleInterogation', 'duration'),
                           ('DipoleInterogation', 'frequency'),
                           ('DipoleInterogation', 'DopplerCoolingSP_power'),
                           ('DipoleInterogation', 'StateDetectionSP_power'),
                           ('DipoleInterogation', 'repump_power')
                           ]

    def sequence(self):
        p = self.parameters
        self.addDDS('369DP',
                    self.start,
                    p.DipoleInterogation.duration,
                    p.DipoleInterogation.frequency,
                    U(-5.0, 'dBm'))
        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.DipoleInterogation.duration,
                    U(110.0, 'MHz'),
                    p.DipoleInterogation.DopplerCoolingSP_power)
        self.addDDS('StateDetectionSP',
                    self.start,
                    p.DipoleInterogation.duration,
                    U(110.0, 'MHz'),
                    p.DipoleInterogation.StateDetectionSP_power)
        self.addDDS('935SP',
                    self.start,
                    p.DipoleInterogation.duration,
                    U(320.0, 'MHz'),
                    p.DipoleInterogation.repump_power)
        self.addTTL('TimeResolvedCount', self.start, p.DipoleInterogation.duration)
        self.end = self.start + p.DipoleInterogation.duration
