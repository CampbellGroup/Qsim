from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class shelving(pulse_sequence):

    required_parameters = [
        ('Shelving', 'duration'),
        ('Shelving', 'assist_power'),
        ('Shelving', 'repump_power'),
        ('Transitions', 'main_cooling_369'),
        ('DopplerCooling', 'detuning'),
        ('ddsDefaults', 'SP411_freq'),
        ('ddsDefaults', 'SP411_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_935_power'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
    ]

    def sequence(self):
        p = self.parameters

        assist_delay = U(10.0, 'ms')

        self.addDDS('369DP',
                    self.start + assist_delay,
                    p.Shelving.duration - assist_delay,
                    p.Transitions.main_cooling_369 / 2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning / 2.0,
                    p.Shelving.assist_power)

        self.addDDS('DopplerCoolingSP',
                    self.start + assist_delay,
                    p.Shelving.duration - assist_delay,
                    p.ddsDefaults.doppler_cooling_freq,
                    p.ddsDefaults.doppler_cooling_power)

        self.addDDS('411SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.SP411_freq,
                    p.ddsDefaults.SP411_power)

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.ddsDefaults.repump_935_power)

        self.end = self.start + p.Shelving.duration
