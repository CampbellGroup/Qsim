from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class interogation_411(pulse_sequence):

    required_parameters = [
                           ('Interogation_411', 'duration'),
                           ('Interogation_411', 'power'),
                           ('Interogation_411', 'assist_power'),
                           ('Interogation_411', 'repump_power')
        
                           ]

    def sequence(self):
        p = self.parameters
        self.addDDS('369DP',
                    self.start,
                    p.Interogation_411.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    p.Interogation_411.assist_power)


        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.Interogation_411.duration,
                    U(110.0, 'MHz'),
                    U(-20.8, 'dBm'))

        self.addDDS('935SP',
                    self.start,
                    p.Interogation_411.duration,
                    U(320.0, 'MHz'),
                    p.Interogation_411.repump_power)

        self.addDDS('411SP',
                    self.start,
                    p.Interogation_411.duration,
                    U(250.0, 'MHz'),
                    p.Interogation_411.power)

        
        self.end = self.start + p.Interogation_411.duration
