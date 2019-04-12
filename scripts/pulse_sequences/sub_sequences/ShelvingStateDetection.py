from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class shelving_state_detection(pulse_sequence):

    required_parameters = [
                           ('ShelvingStateDetection', 'duration'),
                           ('ShelvingStateDetection', 'repump_power'),
                           ('ShelvingStateDetection', 'detuning'),
                           ('ShelvingStateDetection', 'CW_power'),
                           ('Transitions', 'main_cooling_369'),
                           ('Deshelving', 'duration'),
                           ('Deshelving', 'power')
                            ]

    def sequence(self):
        p = self.parameters

        self.addTTL('ReadoutCount',
                    self.start,
                    p.ShelvingStateDetection.duration)
        
        self.addDDS('935SP',
                    self.start,
                    p.ShelvingStateDetection.duration,
                    U(320.0, 'MHz'),
                    p.ShelvingStateDetection.repump_power)

        self.addDDS('369DP',
                    self.start,
                    p.ShelvingStateDetection.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.ShelvingStateDetection.detuning/2.0,
                    p.ShelvingStateDetection.CW_power)
            
        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.ShelvingStateDetection.duration,
                    U(110.0, 'MHz'),
                    U(-20.8, 'dBm'))

            # state readout, deshelve
        self.addDDS('760SP',
                    self.start + U(100.0, 'us') + p.ShelvingStateDetection.duration,
                    p.Deshelving.duration,
                    U(320.0, 'MHz'),
                    p.Deshelving.power)

        self.end = self.start + p.ShelvingStateDetection.duration + U(100.0, 'us') + p.Deshelving.duration
