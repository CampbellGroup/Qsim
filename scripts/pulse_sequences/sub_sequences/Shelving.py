from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class shelving(pulse_sequence):

    required_parameters = [
        ('Shelving', 'duration'),
        ('Shelving', 'assist_power'),
        ('Shelving', 'repump_power'),
        ('Transitions', 'main_cooling_369'),
        ('DopplerCooling', 'detuning'),
        ('MicrowaveInterogation', 'power'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('ddsDefaults', 'SP411_freq'),
        ('ddsDefaults', 'SP411_power')
    ]

    def sequence(self):
        p = self.parameters
        shutterlag = U(2.0, 'ms')

        # variable amount of assist time put in so that when we try to prepare the
        # metastable qubit, the first photon will benefit from |1> preparation,
        # but additonal scattering events wont leave the ion stuck in the |0>
        if p.Shelving.duration['ms'] > 20.0:
            assist_start = self.start + U(10.0, 'ms')
            assist_duration = p.Shelving.duration - U(10.0, 'ms')

        elif p.Shelving.duration['ms'] <= 20.0:
            assist_start = self.start
            assist_duration = p.Shelving.duration

        # hard coded off for high fidelity experiment fears
        #self.addDDS('369DP',
        #            assist_start,
        #            assist_duration,
        #            p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
        #            U(-46.0, 'dBm'))

        #self.addDDS('DopplerCoolingSP',
        #            assist_start,
        #            assist_duration,
        #            p.ddsDefaults.doppler_cooling_freq,
        #            p.ddsDefaults.doppler_cooling_power)

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.Shelving.repump_power)

        self.addDDS('411SP',
                    self.start,
                    p.Shelving.duration,
                    p.ddsDefaults.SP411_freq,
                    p.ddsDefaults.SP411_power)


        #if p.Shelving.duration > shutterlag:
        #    self.addTTL('ShelvingShutter',
        #                self.start,
        #                p.Shelving.duration)

        self.end = self.start + p.Shelving.duration
