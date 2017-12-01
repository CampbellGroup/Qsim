from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class doppler_cooling(pulse_sequence):

    required_parameters = [
                           ('DopplerCooling', 'cooling_power'),
                           ('DopplerCooling', 'repump_power'),
                           ('DopplerCooling', 'detuning'),
                           ('DopplerCooling', 'duration'),
                           ('Transitions', 'main_cooling_369')
                           ]

    def sequence(self):
        p = self.parameters

        #self.addDDS('DopplerCoolingSP',
        #            self.start,
        #            p.DopplerCooling.duration,
        #            U(110.0, 'MHz'),
        #            p.DopplerCooling.cooling_power)

        self.addDDS('369DP',
                    self.start,
                    p.DopplerCooling.duration,
                    p.Transitions.main_cooling_369 + p.DopplerCooling.detuning/2.0,
                    p.DopplerCooling.cooling_power)

        self.addDDS('935SP',
                    self.start,
                    p.DopplerCooling.duration,
                    U(320.0, 'MHz'),
                    p.DopplerCooling.repump_power)

        self.end = self.start + p.DopplerCooling.duration
