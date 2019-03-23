from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class bright_state_pumping(pulse_sequence):

    required_parameters = [
                           ('BrightStatePumping', 'doppler_power'),
                           ('BrightStatePumping', 'repump_power'),
                           ('BrightStatePumping', 'detuning'),
                           ('BrightStatePumping', 'duration'),
                           ('BrightStatePumping', 'bright_prep_method'),
                           ('Transitions', 'main_cooling_369'),
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('Line_Selection', 'qubit'),
                           ('Transitions', 'qubit_0'),
                           ('Transitions', 'qubit_plus'),
                           ('Transitions', 'qubit_minus'),
                           ('OpticalPumping', 'duration'),
                           ('OpticalPumping', 'power'),
                           ('OpticalPumping', 'detuning'),
                           ('OpticalPumping', 'repump_power')
                           ]

    def sequence(self):
        p = self.parameters
        
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

            if p.Line_Selection.qubit == 'qubit_0':
                center = p.Transitions.qubit_0

            elif p.Line_Selection.qubit == 'qubit_plus':
                center = p.Transitions.qubit_plus

            elif p.Line_Selection.qubit == 'qubit_minus':
                center = p.Transitions.qubit_minus


            self.addDDS('OpticalPumpingSP',
                        self.start,
                        p.OpticalPumping.duration,
                        U(110.0 + 4.0, 'MHz'),
                        U(-18.4, 'dBm'))

            self.addDDS('369DP',
                        self.start,
                        p.OpticalPumping.duration,
                        p.Transitions.main_cooling_369/2 + U(200.0 - 4.0/2.0, 'MHz') + p.OpticalPumping.detuning/2.0,
                        p.OpticalPumping.power)

            self.addDDS('935SP',
                        self.start,
                        p.OpticalPumping.duration,
                        U(320.0, 'MHz'),
                        p.OpticalPumping.repump_power)

            DDS_freq = U(197.188, 'MHz') - (p.MicrowaveInterogation.detuning + center)
            self.addDDS('Microwave_qubit',
                        self.start + p.OpticalPumping.duration,
                        p.MicrowaveInterogation.duration,
                        DDS_freq,
                        U(6.0, 'dBm'))

            self.end = self.start + p.OpticalPumping.duration + p.MicrowaveInterogation.duration
