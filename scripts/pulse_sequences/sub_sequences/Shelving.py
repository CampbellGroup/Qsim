from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class shelving(pulse_sequence):

    required_parameters = [
                           ('Shelving', 'duration'),
                           ('Shelving', 'cooling_assist_power'),
                           ('DopplerCooling', 'cooling_power'),
                           ('DopplerCooling', 'repump_power'),
                           ('DopplerCooling', 'detuning'),
                           ('Transitions', 'main_cooling_369')
                           ]

    def sequence(self):
        p = self.parameters
        self.addTTL('MicrowaveTTL', self.start, p.Shelving.duration)
        self.end = self.start + p.Shelving.duration

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.Shelving.duration,
                    U(110.0, 'MHz'),
                    p.Shelving.cooling_assist_power)

        self.addDDS('369DP',
                    self.start,
                    p.Shelving.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    U(-5.0, 'dBm'))

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    U(320.0, 'MHz'),
                    p.DopplerCooling.repump_power)

