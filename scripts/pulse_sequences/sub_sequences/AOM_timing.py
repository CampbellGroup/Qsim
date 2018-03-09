from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.TurnOffAll import turn_off_all
from labrad.units import WithUnit as U


class AOM_fitting(pulse_sequence):

    required_parameters = [
                           ('AOMTiming', 'AOM'),
                           ('AOMTiming', 'duration'),
                           ('AOMTiming', 'frequency'),
                           ('AOMTiming', 'power')
                           ]

    required_subsequences = [turn_off_all]

    def sequence(self):
        p = self.parameters

        self.addSequence(turn_off_all)

        self.addDDS('369DP',
                    self.start,
                    p.AOMTiming.duration,
                    U(200.0, 'MHz'),
                    U(-5.0, 'dBm'))

        self.addDDS(p.AOMTiming.AOM,
                    self.start,
                    p.AOMTiming.duration,
                    p.AOMTiming.frequency,
                    p.AOMTiming.power)
        self.addTTL('TimeResolvedCount', self.start, self.end)
