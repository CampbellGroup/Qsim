from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from config.pulser.hardwareConfiguration import hardwareConfiguration as hc
from labrad.units import WithUnit


class TurnOffAll(PulseSequence):
    def sequence(self):
        dur = WithUnit(1., 'us')
        for channel in hc.ddsDict.keys():
            if channel not in ['RF_Drive', 'Microwave_qubit']:
                self.add_dds(channel, self.start, dur,
                             WithUnit(0, 'MHz'), WithUnit(-46.0, 'dBm'))
        self.end = self.start + dur
