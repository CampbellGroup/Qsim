from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class shelving_state_detection(pulse_sequence):

    required_parameters = [
                           ('StateDetection', 'duration'),
                           ('StateDetection', 'repump_power'),
                           ('StateDetection', 'detuning'),
                           ('StateDetection', 'CW_power'),
                           ('Transitions', 'main_cooling_369'),
                           ('Deshelving', 'duration'),
                           ('Deshelving', 'power')
                            ]

    def sequence(self):
        p = self.parameters

        self.addTTL('ReadoutCount',
                    self.start,
                    p.StateDetection.duration)
        
        self.addDDS('935SP',
                    self.start,
                    p.StateDetection.duration,
                    U(320.0, 'MHz'),
                    p.StateDetection.repump_power)

        self.addDDS('369DP',
                    self.start,
                    p.StateDetection.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.StateDetection.detuning,
                    p.StateDetection.CW_power)
            
        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.StateDetection.duration,
                    U(116.7, 'MHz'),
                    U(-20.8, 'dBm'))

            # state readout, deshelve
        self.addDDS('760SP',
                    self.start + U(100.0, 'us') + p.StateDetection.duration,
                    p.Deshelving.duration,
                    U(320.0, 'MHz'),
                    p.Deshelving.power)

        self.end = self.start + p.StateDetection.duration + U(100.0, 'us') + p.Deshelving.duration
