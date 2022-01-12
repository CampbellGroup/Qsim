from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.MicrowaveInterrogation import microwave_interrogation
from Qsim.scripts.pulse_sequences.sub_sequences.OpticalPumping import optical_pumping
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.Hadamard import hadamard
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.MicrowaveSequenceStandard_RandomPhase import microwave_sequence_standard_random_phase
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
                             hadamard, microwave_sequence_standard_random_phase]

    def sequence(self):
        p = self.parameters
        # self.end = self.start + p.BrightStatePumping.duration

        if p.BrightStatePumping.bright_prep_method == 'Doppler Cooling':
            self.addTTL('WindfreakSynthHDTTL',
                        self.start,
                        p.BrightStatePumping.duration)
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

        elif p.BrightStatePumping.bright_prep_method == 'Doppler Cooling Fiber EOM':
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
            if p.BrightStatePumping.start_with_Hadamard == 'On':
                print 'adding Hadamard gate'
                self.addSequence(hadamard)
            if p.BrightStatePumping.microwave_phase_list == 'constant':
                for i in range(int(p.MicrowaveInterrogation.repetitions)):
                    self.addSequence(microwave_interrogation)
            elif p.BrightStatePumping.microwave_phase_list == 'random':
                for i in range(int(p.MicrowaveInterrogation.repetitions)):
                    self.addSequence(microwave_sequence_standard_random_phase)
