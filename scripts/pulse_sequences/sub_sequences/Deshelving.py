from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class deshelving(pulse_sequence):

    required_parameters = [
        ('Deshelving', 'duration'),
        ('Deshelving', 'power1'),
        ('Deshelving', 'power2'),
        ('DopplerCooling', 'cooling_power'),
        ('DopplerCooling', 'detuning'),
        ('Transitions', 'main_cooling_369'),
        ('Deshelving', 'repump_power'),
        ('MicrowaveInterogation', 'power'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_2_freq'),
        ('ddsDefaults', 'qubit_dds_freq')
                           ]

    def sequence(self):
        p = self.parameters

        self.addDDS('369DP',
                    self.start,
                    p.Deshelving.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    p.DopplerCooling.cooling_power)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.Deshelving.duration,
                    p.ddsDefaults.doppler_cooling_freq,
                    p.ddsDefaults.doppler_cooling_power)

        self.addDDS('935SP',
                    self.start,
                    p.Deshelving.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.Deshelving.repump_power)

        self.addDDS('760SP',
                    self.start,
                    p.Deshelving.duration,
                    p.ddsDefaults.repump_760_1_freq,
                    p.Deshelving.power1)

        self.addDDS('760SP2',
                    self.start,
                    p.Deshelving.duration,
                    p.ddsDefaults.repump_760_2_freq,
                    p.Deshelving.power2)

        self.addTTL('976SP',
                    self.start,
                    p.Deshelving.duration)

        #self.addTTL('MicrowaveTTL',
        #            self.start,
        #            p.Deshelving.duration)
        self.addDDS('Microwave_qubit',
                    self.start,
                    p.Deshelving.duration,
                    U(362.0, 'MHz'),
                    p.MicrowaveInterogation.power)

        self.end = self.start + p.Deshelving.duration
