from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class dipole_interrogation(pulse_sequence):

    required_parameters = [
        ('DipoleInterrogation', 'duration'),
        ('DipoleInterrogation', 'frequency'),
        ('DipoleInterrogation', 'power'),
        ('DipoleInterrogation', 'repump_power'),
        ('DipoleInterrogation', 'interrogation_laser'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'optical_pumping_freq'),
        ('ddsDefaults', 'state_detection_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'optical_pumping_power'),
        ('ddsDefaults', 'state_detection_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_976_freq'),
        ('ddsDefaults', 'repump_976_power'),
        ('ddsDefaults', 'DP369_freq')
    ]

    def sequence(self):
        p = self.parameters
        self.addDDS('369DP',
                    self.start,
                    p.DipoleInterrogation.duration,
                    p.DipoleInterrogation.frequency,
                    p.DipoleInterrogation.power)

        if p.DipoleInterrogation.interrogation_laser == 'DopplerCoolingSP':
            self.addDDS('DopplerCoolingSP',
                        self.start,
                        p.DipoleInterrogation.duration,
                        p.ddsDefaults.doppler_cooling_freq,
                        p.ddsDefaults.doppler_cooling_power)

        if p.DipoleInterrogation.interrogation_laser == 'StateDetectionSP':
            self.addDDS('StateDetectionSP',
                        self.start,
                        p.DipoleInterrogation.duration,
                        p.ddsDefaults.state_detection_freq,
                        p.ddsDefaults.state_detection_power)

        if p.DipoleInterrogation.interrogation_laser == 'OpticalPumpingSP':
            self.addDDS('OpticalPumpingSP',
                        self.start,
                        p.DipoleInterrogation.duration,
                        p.ddsDefaults.optical_pumping_freq,
                        p.ddsDefaults.optical_pumping_power)

        self.addDDS('935SP',
                    self.start,
                    p.DipoleInterrogation.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.DipoleInterrogation.repump_power)

        self.addDDS('976SP',
                    self.start,
                    p.DipoleInterrogation.duration,
                    p.ddsDefaults.repump_976_freq,
                    p.ddsDefaults.repump_976_power)

        self.addTTL('TimeResolvedCount', self.start, p.DipoleInterrogation.duration)
        self.end = self.start + p.DipoleInterrogation.duration
