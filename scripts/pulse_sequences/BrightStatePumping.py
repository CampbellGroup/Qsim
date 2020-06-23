from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.MicrowaveInterogation import microwave_interogation
from Qsim.scripts.pulse_sequences.sub_sequences.DoubleMicrowaveInterogation import double_microwave_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.OpticalPumping import optical_pumping
from labrad.units import WithUnit as U
import numpy as np


class bright_state_pumping(pulse_sequence):

    required_parameters = [
        ('BrightStatePumping', 'doppler_power'),
        ('BrightStatePumping', 'repump_power'),
        ('BrightStatePumping', 'detuning'),
        ('BrightStatePumping', 'duration'),
        ('BrightStatePumping', 'bright_prep_method'),
        ('BrightStatePumping', 'microwave_phase_list'),
        ('MicrowaveInterogation', 'repititions'),
        ('MicrowaveInterogation', 'microwave_phase'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
                           ]

    required_subsequences = [optical_pumping, microwave_interogation, double_microwave_sequence]

    def sequence(self):
        p = self.parameters
        self.end = self.start + p.BrightStatePumping.duration

        if p.BrightStatePumping.bright_prep_method == 'Doppler Cooling':
            self.addDDS('DopplerCoolingSP',
                        self.start,
                        p.BrightStatePumping.duration,
                        p.ddsDefaults.doppler_cooling_freq,
                        p.ddsDefaults.doppler_cooling_power)

            self.addDDS('369DP',
                        self.start,
                        p.BrightStatePumping.duration,
                        p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.BrightStatePumping.detuning/2.0,
                        p.BrightStatePumping.doppler_power)

            self.addDDS('935SP',
                        self.start,
                        p.BrightStatePumping.duration,
                        p.ddsDefaults.repump_935_freq,
                        p.BrightStatePumping.repump_power)

            self.end = self.start + p.BrightStatePumping.duration

        elif p.BrightStatePumping.bright_prep_method == 'Microwave':
            self.addSequence(optical_pumping)

            if p.BrightStatePumping.microwave_phase_list == 'constant':
                phases = np.zeros(int(p.MicrowaveInterogation.repititions))
            elif p.BrightStatePumping.microwave_phase_list == 'random':
                phases = 360.0*np.random.rand(int(p.MicrowaveInterogation.repititions))
            elif p.BrightStatePumping.microwave_phase_list == 'zeroPizero':
                phases = 180.0 * np.array([i % 2 for i in range(int(p.MicrowaveInterogation.repititions))])

            for i in range(int(p.MicrowaveInterogation.repititions)):
                p['MicrowaveInterogation.microwave_phase'] = U(phases[i], 'deg')
                self.addSequence(microwave_interogation)

        # double microwave is programmed separately b/c PI_times are hard coded, not variable
        elif p.BrightStatePumping.bright_prep_method == 'Double_Microwave':
            self.addSequence(optical_pumping)
            self.addSequence(double_microwave_sequence)
