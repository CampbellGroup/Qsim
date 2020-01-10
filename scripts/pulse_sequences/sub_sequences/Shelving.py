from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class shelving(pulse_sequence):

    required_parameters = [
                           ('Shelving', 'duration'),
                           ('Shelving', 'power'),
                           ('Shelving', 'detuning'),
                           ('Shelving', 'assist_power'),
                           ('Shelving', 'repump_power'),
                           ('Transitions', 'main_cooling_369'),
                           ('DopplerCooling', 'detuning')
                           ]

    def sequence(self):
        p = self.parameters
        shutterlag = U(2.0, 'ms')

        self.addDDS('369DP',
                    self.start,
                    p.Shelving.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    U(-46.0, 'dBm'))

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.Shelving.duration,
                    U(110.0, 'MHz'),
                    U(-46.0, 'dBm'))  # shelving assist hard coded to 0 for leakthrough concerns

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    U(320.0, 'MHz'),
                    p.Shelving.repump_power)

        self.addDDS('411DP',
                    self.start,
                    p.Shelving.duration,
                    U(250.0, 'MHz'),
                    p.Shelving.power)

        if p.Shelving.duration > shutterlag:
            self.addTTL('ShelvingShutter',
                        self.start,
                        p.Shelving.duration)

        self.end = self.start + p.Shelving.duration
