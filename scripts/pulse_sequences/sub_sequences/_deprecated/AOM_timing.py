from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from Qsim.scripts.pulse_sequences.microwave_point import microwave_point
from labrad.units import WithUnit as U


class AOM_fitting(PulseSequence):

    required_parameters = [
#                           ('AOMTiming', 'AOM'),
#                           ('AOMTiming', 'duration'),
#                           ('AOMTiming', 'frequency'),
#                           ('AOMTiming', 'power')
                           ]

    required_subsequences = [microwave_point]

    def sequence(self):
        p = self.parameters

#        self.addDDS('369DP',
#                    self.start,
#                    p.AOMTiming.duration,
#                    U(200.0, 'MHz'),
#                    U(-5.0, 'dBm'))

#        self.addDDS(p.AOMTiming.AOM,
#                    self.start,
#                    p.AOMTiming.duration,
#                    p.AOMTiming.frequency,
#                    p.AOMTiming.power)
        init_start = self.start
        self.add_sequence(microwave_point)
        self.add_ttl('TimeResolvedCount', init_start, self.end - init_start)
#        self.end = self.start + p.AOMTiming.duration + U(10.0, 'us')
