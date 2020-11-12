from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class shelving(pulse_sequence):

    required_parameters = [
        ('Shelving', 'duration'),
        ('Shelving', 'assist_power'),
        ('Shelving', 'repump_power'),
        ('Shelving', 'assist_laser'),
        ('Transitions', 'main_cooling_369'),
        ('Transitions', 'quadrupole'),
        ('DopplerCooling', 'detuning'),
        ('OpticalPumping', 'detuning'),
        ('ddsDefaults', 'DP411_freq'),
        ('ddsDefaults', 'DP411_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_935_power'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'optical_pumping_freq'),
        ('ddsDefaults', 'optical_pumping_power'),
        ('ddsDefaults', 'DP369_freq')
    ]

    def sequence(self):
        p = self.parameters

        assist_delay = U(7.0, 'ms')

        if p.Shelving.duration > assist_delay and p.Shelving.assist_laser != 'None':
            if p.Shelving.assist_laser == 'Doppler Cooling':

                self.addDDS('369DP',
                            self.start + assist_delay,
                            p.Shelving.duration - assist_delay,
                            p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.DopplerCooling.detuning / 2.0,
                            p.Shelving.assist_power)

                self.addDDS('DopplerCoolingSP',
                            self.start + assist_delay,
                            p.Shelving.duration - assist_delay,
                            p.ddsDefaults.doppler_cooling_freq,
                            p.ddsDefaults.doppler_cooling_power)

            elif p.Shelving.assist_laser == 'Optical Pumping':
                
                self.addDDS('369DP',
                            self.start + assist_delay,
                            p.Shelving.duration - assist_delay,
                            p.Transitions.main_cooling_369 / 2.0 + p.ddsDefaults.DP369_freq + p.OpticalPumping.detuning / 2.0,
                            p.Shelving.assist_power)

                self.addDDS('OpticalPumpingSP',
                            self.start + assist_delay,
                            p.Shelving.duration - assist_delay,
                            p.ddsDefaults.optical_pumping_freq,
                            p.ddsDefaults.optical_pumping_power)

        self.addDDS('411DP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.DP411_freq - p.Transitions.quadrupole,  # minus sign reflects the way the quadrupole line scan exp is written
                    p.ddsDefaults.DP411_power)

        self.addTTL('861SP',
                    self.start,
                    p.Shelving.duration)

        self.end = self.start + p.Shelving.duration
