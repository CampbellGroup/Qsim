from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class bright_state_pumping(pulse_sequence):

    required_parameters = [
                           ('BrightStatePumping', 'doppler_power'),
                           ('BrightStatePumping', 'repump_power'),
                           ('BrightStatePumping', 'detuning'),
                           ('BrightStatePumping', 'duration'),
                           ('Transitions', 'main_cooling_369')
                           ]

    def sequence(self):
        p = self.parameters

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.BrightStatePumping.duration,
                    U(110.0, 'MHz'),
                    p.BrightStatePumping.doppler_power)

        self.addDDS('369DP',
                    self.start,
                    p.BrightStatePumping.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.BrightStatePumping.detuning/2.0,
                    U(-5.0, 'dBm'))

        self.addDDS('935SP',
                    self.start,
                    p.BrightStatePumping.duration,
                    U(320.0, 'MHz'),
                    p.BrightStatePumping.repump_power)

        self.end = self.start + p.BrightStatePumping.duration
