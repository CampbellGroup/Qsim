from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.MicrowaveInterrogation import microwave_interrogation
from Qsim.scripts.pulse_sequences.sub_sequences.OpticalPumping import optical_pumping
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.Hadamard import hadamard
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
        ('BrightStatePumping', 'start_with_Hadamard'),
        ('MicrowaveInterrogation', 'repetitions'),
        ('MicrowaveInterrogation', 'microwave_phase'),
        ('Transitions', 'main_cooling_369'),
        ('ddsDefaults', 'doppler_cooling_freq'),
        ('ddsDefaults', 'doppler_cooling_power'),
        ('ddsDefaults', 'repump_935_freq'),
                           ]

    required_subsequences = [optical_pumping, microwave_interrogation,
                             hadamard]

    def sequence(self):
        p = self.parameters
        # self.end = self.start + p.BrightStatePumping.duration

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
                phases = np.zeros(int(p.MicrowaveInterrogation.repetitions))
            elif p.BrightStatePumping.microwave_phase_list == 'random':
                phases = 360.0*np.random.rand(int(p.MicrowaveInterrogation.repetitions))
            elif p.BrightStatePumping.microwave_phase_list == 'zeroPizero':
                phases = 180.0 * np.array([i % 2 for i in range(int(p.MicrowaveInterrogation.repetitions))])

            if p.BrightStatePumping.start_with_Hadamard == 'On':
                print 'adding Hadamrad gate'
                self.addSequence(hadamard)

            for i in range(int(p.MicrowaveInterrogation.repetitions)):
                p['MicrowaveInterrogation.microwave_phase'] = U(phases[i], 'deg')
                self.addSequence(microwave_interrogation)
