from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class shelving(pulse_sequence):

    required_parameters = [
                           ('Shelving', 'duration'),
                           ('Shelving', 'power'),
                           ('Shelving', 'detuning'),
                           ('Shelving', 'assist_power'),
                           ('Shelving', 'repump_power'),
                           ('Transitions', 'main_cooling_369'),
                           ('DopplerCooling', 'detuning')
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

        self.addDDS('369DP',
                    assist_start,
                    assist_duration,
                    p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.DopplerCooling.detuning/2.0,
                    p.Shelving.assist_power)

        self.addDDS('DopplerCoolingSP',
                    assist_start,
                    assist_duration,
                    U(110.0, 'MHz'),
                    U(-9.0, 'dBm'))

        self.addDDS('935SP',
                    self.start,
                    p.Shelving.duration,
                    U(320.0, 'MHz'),
                    p.Shelving.repump_power)

        self.addTTL('411TTL',
                    self.start,
                    p.Shelving.duration)

        if p.Shelving.duration > shutterlag:
            self.addTTL('ShelvingShutter',
                        self.start,
                        p.Shelving.duration)

        self.end = self.start + p.Shelving.duration
