from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from config.pulser.hardwareConfiguration import hardwareConfiguration as hc
from labrad.units import WithUnit


class turn_off_all(pulse_sequence):
        def sequence(self):
                dur = WithUnit(1., 'us')
                for channel in hc.ddsDict.keys():
                        if channel not in ['RF_Drive', 'Microwave_qubit']:
                                self.addDDS(channel, self.start, dur,
                                            WithUnit(0, 'MHz'), WithUnit(-46.0, 'dBm'))
                self.end = self.start + dur
