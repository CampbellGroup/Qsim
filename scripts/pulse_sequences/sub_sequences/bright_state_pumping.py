from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import MicrowaveInterrogation
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import OpticalPumping
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.Hadamard import Hadamard
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.microwave_sequence_standard_random_phase import MicrowaveSequenceStandardRandomPhase
from labrad.units import WithUnit as U


class BrightStatePumping(pulse_sequence):

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
        ('ddsDefaults', 'repump_976_freq'),
        ('ddsDefaults', 'repump_976_power'),
        ('Modes', 'bright_state_pumping')
                           ]

    required_subsequences = [OpticalPumping, MicrowaveInterrogation,
                             Hadamard, MicrowaveSequenceStandardRandomPhase]

    def sequence(self):
        p = self.parameters

        prep_method = p.Modes.bright_state_pumping
        laser_mode = p.Modes.laser_369

        if prep_method == 'Doppler Cooling':
            if laser_mode == 'FiberEOM':
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
                self.addDDS('976SP',
                            self.start,
                            p.BrightStatePumping.duration,
                            p.ddsDefaults.repump_976_freq,
                            p.ddsDefaults.repump_976_power)
                self.end = self.start + p.BrightStatePumping.duration

            elif laser_mode == 'FiberEOM173':
                # self.addTTL('WindfreakSynthHDTTL',
                #             self.start,
                #             p.BrightStatePumping.duration)
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
                self.addDDS('976SP',
                            self.start,
                            p.BrightStatePumping.duration,
                            p.ddsDefaults.repump_976_freq,
                            p.ddsDefaults.repump_976_power)
                self.end = self.start + p.BrightStatePumping.duration

            elif laser_mode == 'Standard':
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

        elif prep_method == 'Microwave':
            self.addSequence(OpticalPumping)
            if p.BrightStatePumping.start_with_Hadamard == 'On':
                print('adding Hadamard gate')
                self.addSequence(Hadamard)
            if p.BrightStatePumping.microwave_phase_list == 'constant':
                for i in range(int(p.MicrowaveInterrogation.repetitions)):
                    self.addSequence(MicrowaveInterrogation)
            elif p.BrightStatePumping.microwave_phase_list == 'random':
                for i in range(int(p.MicrowaveInterrogation.repetitions)):
                    self.addSequence(MicrowaveSequenceStandardRandomPhase)
