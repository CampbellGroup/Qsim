from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class deshelving(pulse_sequence):

    required_parameters = [
        ('Deshelving', 'duration'),
        ('Deshelving', 'power1'),
        ('Deshelving', 'power2'),
        ('DopplerCooling', 'cooling_power'),
        ('DopplerCooling', 'detuning'),
        ('Transitions', 'main_cooling_369'),
        ('Deshelving', 'repump_power'),
        ('ddsDefaults', 'doppler_cooling_freq')

                           ]

    def sequence(self):
        p = self.parameters

        self.addDDS('369DP',
                    self.start,
                    p.Deshelving.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    p.DopplerCooling.cooling_power)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.Deshelving.duration,
                    p.ddsDefaults.doppler_cooling_freq,
                    U(-9.0, 'dBm'))

        self.addDDS('935SP',
                    self.start,
                    p.Deshelving.duration,
                    U(320.0, 'MHz'),
                    p.Deshelving.repump_power)

        self.addDDS('760SP',
                    self.start,
                    p.Deshelving.duration,
                    U(160.0, 'MHz'),
                    p.Deshelving.power1)

        self.addDDS('760SP2',
                    self.start,
                    p.Deshelving.duration,
                    U(160.0, 'MHz'),
                    p.Deshelving.power2)

        self.end = self.start + p.Deshelving.duration
