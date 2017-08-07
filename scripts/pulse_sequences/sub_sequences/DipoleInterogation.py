from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

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
                    U(-5.0, 'dBm'))
        self.addDDS('Doppler Cooling (14 GHz)',
                    self.start,
                    p.DipoleInterogation.duration,
                    U(110.0, 'MHz'),
                    p.DipoleInterogation.power)
        self.addDDS('repump',
                    self.start,
                    p.DipoleInterogation.duration,
                    U(320.0, 'MHz'),
                    U(-0.1, 'dBm'))
        self.addTTL('TimeResolvedCount', self.start, p.DipoleInterogation.duration)
        self.end = self.start + p.DipoleInterogation.duration
