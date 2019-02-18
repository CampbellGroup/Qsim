from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class optical_pumping(pulse_sequence):

    required_parameters = [
                           ('OpticalPumping', 'duration'),
                           ('OpticalPumping', 'power'),
                           ('OpticalPumping', 'detuning'),
                           ('OpticalPumping', 'repump_power'),
                           ('StateDetection', 'mode'),
                           ('Shelving', 'duration'),
                           ('Shelving', 'power'),
                           ('Shelving', 'cooling_assist_power'),
                           ('Transitions', 'main_cooling_369'),
                           ('DopplerCooling', 'detuning')
                           ]

    def sequence(self):
        p = self.parameters


        
        if p.StateDetection.mode == 'Shelving':
            self.addDDS('411SP',
            self.start,
            p.Shelving.duration,
            U(250.0, 'MHz'),
            p.Shelving.power)
    
            self.addDDS('369DP',
                        self.start,
                        p.Shelving.duration,
                        p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                        p.Shelving.cooling_assist_power)
            self.addDDS('DopplerCoolingSP',
                        self.start,
                        p.Shelving.duration,
                        U(110.0, 'MHz'),
                        U(-20.8, 'dBm'))
            self.addDDS('935SP',
                        self.start,
                        p.Shelving.duration,
                        U(320.0, 'MHz'),
                        p.OpticalPumping.repump_power)

            self.end = self.start + p.Shelving.duration


        else:
            self.addDDS('OpticalPumpingSP',
                        self.start,
                        p.OpticalPumping.duration,
                        U(110.0 + 4.0, 'MHz'),
                        U(-18.4, 'dBm'))

            self.addDDS('369DP',
                        self.start,
                        p.OpticalPumping.duration,
                        p.Transitions.main_cooling_369/2 + U(200.0 - 4.0/2.0, 'MHz') + p.OpticalPumping.detuning/2.0,
                        p.OpticalPumping.power)

            self.addDDS('935SP',
                        self.start,
                        p.OpticalPumping.duration,
                        U(320.0, 'MHz'),
                        p.OpticalPumping.repump_power)
            self.end = self.start + p.OpticalPumping.duration
