from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class shelving_doppler_cooling(pulse_sequence):

    required_parameters = [
        ('DopplerCooling', 'cooling_power'),
        ('DopplerCooling', 'repump_power'),
        ('DopplerCooling', 'detuning'),
        ('Shelving_Doppler_Cooling', 'duration'),
        ('Transitions', 'main_cooling_369'),
        ('MicrowaveInterogation', 'power'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'repump_760_1_freq'),
        ('ddsDefaults', 'repump_760_1_power'),
        ('ddsDefaults', 'repump_760_2_freq'),
        ('ddsDefaults', 'repump_760_2_power'),
        ('ddsDefaults', 'qubit_dds_freq')
    ]

    def sequence(self):
        p = self.parameters

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.Shelving_Doppler_Cooling.duration,
                    p.ddsDefaults.doppler_cooling_freq,
                    p.ddsDefaults.doppler_cooling_power)

        self.addDDS('369DP',
                    self.start,
                    p.Shelving_Doppler_Cooling.duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    p.DopplerCooling.cooling_power)

        self.addDDS('935SP',
                    self.start,
                    p.Shelving_Doppler_Cooling.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.DopplerCooling.repump_power)

        self.addDDS('760SP',
                    self.start,
                    p.Shelving_Doppler_Cooling.duration,
                    p.ddsDefaults.repump_760_1_freq,
                    p.ddsDefaults.repump_760_1_power)

        self.addDDS('760SP2',
                    self.start,
                    p.Shelving_Doppler_Cooling.duration,
                    p.ddsDefaults.repump_760_2_freq,
                    p.ddsDefaults.repump_760_2_power)

        self.addDDS('Microwave_qubit',
                    self.start,
                    p.Shelving_Doppler_Cooling.duration,
                    p.ddsDefaults.qubit_dds_freq - U(15.0, 'MHz'),
                    p.MicrowaveInterogation.power)

        self.addTTL('ReadoutCount', self.start, p.Shelving_Doppler_Cooling.duration)

        self.end = self.start + p.Shelving_Doppler_Cooling.duration
