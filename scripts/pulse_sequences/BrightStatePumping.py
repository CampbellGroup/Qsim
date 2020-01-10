from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.MicrowaveInterogation import microwave_interogation
from Qsim.scripts.pulse_sequences.sub_sequences.DoubleMicrowaveInterogation import double_microwave_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.OpticalPumping import optical_pumping
from labrad.units import WithUnit as U


class bright_state_pumping(pulse_sequence):

    required_parameters = [
                           ('BrightStatePumping', 'doppler_power'),
                           ('BrightStatePumping', 'repump_power'),
                           ('BrightStatePumping', 'detuning'),
                           ('BrightStatePumping', 'duration'),
                           ('BrightStatePumping', 'bright_prep_method'),
                           ('Transitions', 'main_cooling_369'),
                           ]

    required_subsequences = [optical_pumping, microwave_interogation, double_microwave_sequence]

    def sequence(self):
        p = self.parameters
        self.end = self.start + p.BrightStatePumping.duration

        if p.BrightStatePumping.bright_prep_method == 'Doppler Cooling':
            self.addDDS('DopplerCoolingSP',
                        self.start,
                        p.BrightStatePumping.duration,
                        U(110.0, 'MHz'),
                        U(-20.8, 'dBm'))

            self.addDDS('369DP',
                        self.start,
                        p.BrightStatePumping.duration,
                        p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz') + p.BrightStatePumping.detuning/2.0,
                        p.BrightStatePumping.doppler_power)

            self.addDDS('935SP',
                        self.start,
                        p.BrightStatePumping.duration,
                        U(320.0, 'MHz'),
                        p.BrightStatePumping.repump_power)

            self.end = self.start + p.BrightStatePumping.duration

        elif p.BrightStatePumping.bright_prep_method == 'Microwave':
            self.addSequence(optical_pumping)
            self.addSequence(microwave_interogation)

        # double microwave is programmed separately b/c PI_times are hard coded, not variable
        elif p.BrightStatePumping.bright_prep_method == 'Double_Microwave':
            self.addSequence(optical_pumping)
            self.addSequence(double_microwave_sequence)
