from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class raman_411_interogation(pulse_sequence):

    required_parameters = [
                           ('Raman411Interogation', 'duration'),
                           ('Raman411Interogation', 'detuning1'),
                           ('Raman411Interogation', 'detuning2'),
                           ('Raman411Interogation', 'power1'),
                           ('Raman411Interogation', 'power2'),
                           ]

    def sequence(self):

        p = self.parameters
        DDS_freq_1 = U(250.0, 'MHz') + p.Raman411Interogation.detuning1/2.0
        DDS_freq_2 = U(250.0, 'MHz') + p.Raman411Interogation.detuning2/2.0

        self.addDDS('411DP',
                    self.start,
                    p.Raman411Interogation.duration,
                    DDS_freq_1,
                    p.Raman411Interogation.power1)

        self.addDDS('411SP2',
                    self.start,
                    p.Raman411Interogation.duration,
                    DDS_freq_2,
                    p.Raman411Interogation.power2)

        self.addDDS('760SP',
                    self.start,
                    p.Raman411Interogation.duration,
                    U(160.0, 'MHz'),
                    U(-2.0,  'dBm'))

        self.addDDS('760SP2',
                    self.start,
                    p.Raman411Interogation.duration,
                    U(160.0, 'MHz'),
                    U(6.0,  'dBm'))

        self.end = self.start + p.Raman411Interogation.duration
