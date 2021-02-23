from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class shelving(pulse_sequence):

    required_parameters = [
        ('Shelving', 'duration'),
        ('Shelving', 'repump_power'),
        ('Transitions', 'quadrupole'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'DP1_411_freq'),
        ('ddsDefaults', 'DP1_411_power'),
        ('ddsDefaults', 'DP2_411_freq'),
        ('ddsDefaults', 'DP2_411_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_935_power'),
        ('ddsDefaults', 'DP369_freq'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('DopplerCooling', 'cooling_power'),
        ('DopplerCooling', 'repump_power'),
        ('DopplerCooling', 'detuning'),
        ('ddsDefaults', 'optical_pumping_freq'),
        ('ddsDefaults', 'optical_pumping_power'),
    ]

    def sequence(self):
        p = self.parameters

        """
        This is the standard shelving stuff below
        
        self.addDDS('411DP1',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.DP1_411_freq,
                    p.ddsDefaults.DP1_411_power)

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.ddsDefaults.repump_935_power)
        """

        self.addDDS('411DP2',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.DP2_411_freq,
                    p.ddsDefaults.DP2_411_power)

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.ddsDefaults.repump_935_power)

        self.addDDS('OpticalPumpingSP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.optical_pumping_freq,
                    p.ddsDefaults.optical_pumping_power)

        self.addDDS('369DP',
                    self.start,
                    p.Shelving.duration,
                    p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning / 2.0,
                    U(-10.0, 'dBm'))

        self.end = self.start + p.Shelving.duration
