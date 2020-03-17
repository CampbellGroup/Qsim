from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class dipole_interogation(pulse_sequence):

    required_parameters = [
        ('DipoleInterogation', 'duration'),
        ('DipoleInterogation', 'frequency'),
        ('DipoleInterogation', 'power'),
        ('DipoleInterogation', 'repump_power'),
        ('DipoleInterogation', 'interogation_laser'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'optical_pumping_freq'),
        ('ddsDefaults', 'state_detection_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'optical_pumping_power'),
        ('ddsDefaults', 'state_detection_power'),
        ('ddsDefaults', 'repump_935_freq')
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
                        p.ddsDefaults.doppler_cooling_power)

        if p.DipoleInterogation.interogation_laser == 'StateDetectionSP':
            self.addDDS('StateDetectionSP',
                        self.start,
                        p.DipoleInterogation.duration,
                        p.ddsDefaults.state_detection_freq,
                        p.ddsDefaults.state_detection_power)

        if p.DipoleInterogation.interogation_laser == 'OpticalPumpingSP':
            self.addDDS('OpticalPumpingSP',
                        self.start,
                        p.DipoleInterogation.duration,
                        p.ddsDefaults.optical_pumping_freq,
                        p.ddsDefaults.optical_pumping_power)

        self.addDDS('935SP',
                    self.start,
                    p.DipoleInterogation.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.DipoleInterogation.repump_power)
        self.addTTL('TimeResolvedCount', self.start, p.DipoleInterogation.duration)
        self.end = self.start + p.DipoleInterogation.duration
