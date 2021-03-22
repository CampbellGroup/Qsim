from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class manifold_state_detection(pulse_sequence):

    required_parameters = [
        ('ManifoldDetection', 'duration'),
        ('ShelvingStateDetection', 'repump_power'),
        ('ShelvingStateDetection', 'detuning'),
        ('ShelvingStateDetection', 'CW_power'),
        ('ShelvingStateDetection', 'repetitions'),
        ('ShelvingStateDetection', 'state_readout_threshold'),
        ('MicrowaveInterrogation', 'power'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('ddsDefaults', 'DP369_freq'),
        ('ddsDefaults', 'protection_beam_freq'),
        ('ddsDefaults', 'protection_beam_power')
    ]

    def sequence(self):
        p = self.parameters

        # standard readout count TTL, provides number of detected photons
        self.addTTL('ReadoutCount',
                    self.start,
                    p.ManifoldDetection.duration)

        # # provides timetags
        # self.addTTL('TimeResolvedCount',
        #             self.start,
        #             p.ShelvingStateDetection.duration)

        self.addDDS('935SP',
                    self.start,
                    p.ManifoldDetection.duration,
                    p.ddsDefaults.repump_935_freq,
                    p.ShelvingStateDetection.repump_power)

        self.addDDS('369DP',
                    self.start,
                    p.ManifoldDetection.duration,
                    p.Transitions.main_cooling_369/2.0 + p.ddsDefaults.DP369_freq + p.ShelvingStateDetection.detuning/2.0,
                    p.ShelvingStateDetection.CW_power)

        self.addDDS('DopplerCoolingSP',
                    self.start,
                    p.ManifoldDetection.duration,
                    p.ddsDefaults.doppler_cooling_freq,
                    p.ddsDefaults.doppler_cooling_power)

        self.end = self.start + p.ManifoldDetection.duration
