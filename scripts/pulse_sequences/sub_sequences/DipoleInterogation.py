from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class dipole_interogation(pulse_sequence):

    required_parameters = [
        ('DipoleInterogation', 'duration'),
        ('DipoleInterogation', 'frequency'),
        ('DipoleInterogation', 'power'),
        ('DipoleInterogation', 'repump_power'),
        ('DipoleInterogation', 'interogation_laser'),
        ('ddsDefaults', 'doppler_cooling_freq')
                           ]

    def sequence(self):
        p = self.parameters
        self.addDDS('369DP',
                    self.start,
                    p.DipoleInterogation.duration,
                    p.DipoleInterogation.frequency,
                    p.DipoleInterogation.power)

        if p.DipoleInterogation.interogation_laser == 'DopplerCoolingSP':
            self.addDDS('DopplerCoolingSP',
                        self.start,
                        p.DipoleInterogation.duration,
                        p.ddsDefaults.doppler_cooling_freq,
                        U(-9.0, 'dBm'))

        if p.DipoleInterogation.interogation_laser == 'StateDetectionSP':
            self.addDDS('StateDetectionSP',
                        self.start,
                        p.DipoleInterogation.duration,
                        U(110.0, 'MHz'),
                        U(-4.0, 'dBm'))

        if p.DipoleInterogation.interogation_laser == 'OpticalPumpingSP':
            self.addDDS('OpticalPumpingSP',
                        self.start,
                        p.DipoleInterogation.duration,
                        U(110.0, 'MHz'),
                        U(-4.0, 'dBm'))

        self.addDDS('935SP',
                    self.start,
                    p.DipoleInterogation.duration,
                    U(320.0, 'MHz'),
                    p.DipoleInterogation.repump_power)
        self.addTTL('TimeResolvedCount', self.start, p.DipoleInterogation.duration)
        self.end = self.start + p.DipoleInterogation.duration
