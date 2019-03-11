from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class variable_deshelving(pulse_sequence):

    required_parameters = [
                           ('VariableDeshelving', 'duration'),
                           ('Deshelving', 'power'),
                           ('DopplerCooling', 'cooling_power'),
                           ('DopplerCooling', 'detuning'),
                           ('Transitions', 'main_cooling_369'),
                           ('Deshelving', 'repump_power')
        
                           ]

    def sequence(self):
        p = self.parameters

        self.addDDS('369DP',
                    self.start,
                    p.VariableDeshelving.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    p.DopplerCooling.cooling_power)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.VariableDeshelving.duration,
                    U(110.0, 'MHz'),
                    U(-20.8, 'dBm'))

        self.addDDS('935SP',
                    self.start,
                    p.VariableDeshelving.duration,
                    U(320.0, 'MHz'),
                    p.Deshelving.repump_power)

        self.addDDS('760SP',
                    self.start,
                    p.VariableDeshelving.duration,
                    U(320.0, 'MHz'),
                    p.Deshelving.power)
        
        self.end = self.start + p.VariableDeshelving.duration
