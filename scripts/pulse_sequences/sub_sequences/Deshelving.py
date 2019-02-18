from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class deshelving(pulse_sequence):

    required_parameters = [
                           ('Deshelving', 'duration'),
                           ('Deshelving', 'power'),
                           ('DopplerCooling', 'cooling_power'),
                           ('DopplerCooling', 'repump_power'),
                           ('DopplerCooling', 'detuning'),
                           ('Transitions', 'main_cooling_369')
                           ]

    def sequence(self):
        p = self.parameters
        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.Deshelving.duration,
                    U(110.0, 'MHz'),
                    U(-20.8, 'dBm'))

        self.addDDS('369DP',
                    self.start,
                    p.Deshelving.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    p.DopplerCooling.cooling_power)

        self.addDDS('935SP',
                    self.start,
                    p.Deshelving.duration,
                    U(320.0, 'MHz'),
                    p.DopplerCooling.repump_power)

        self.addDDS('760SP',
                    self.start,
                    p.Deshelving.duration,
                    U(320.0, 'MHz'),
                    p.Deshelving.power)
        
        self.end = self.start + p.Deshelving.duration
