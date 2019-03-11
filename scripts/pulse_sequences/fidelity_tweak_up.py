from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.StateDetection import state_detection
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.MicrowaveInterogation import microwave_interogation


class fidelity_tweak_up(pulse_sequence):

    required_subsequences = [shelving_doppler_cooling, doppler_cooling, state_detection,
                             turn_off_all, bright_state_pumping, optical_pumping, microwave_interogation]

    required_parameters = [
                           ('BrightStatePumping', 'bright_prep_method'),('StateDetection', 'mode'),
                           ]

    def sequence(self):
        bright_prep = self.parameters.BrightStatePumping.bright_prep_method
        self.addSequence(turn_off_all)

        if self.parameters.StateDetection.mode == 'Shelving':
            self.addSequence(shelving_doppler_cooling)
        else:
            self.addSequence(doppler_cooling)

        self.addSequence(turn_off_all)        
        if bright_prep == 'Doppler Cooling':
            self.addSequence(bright_state_pumping)
        elif bright_prep == 'Microwave':
            self.addSequence(optical_pumping)
            self.addSequence(turn_off_all)
            self.addSequence(microwave_interogation)
        self.addSequence(turn_off_all)
        self.addSequence(state_detection)
        self.addSequence(turn_off_all)

        if self.parameters.StateDetection.mode == 'Shelving':
            self.addSequence(shelving_doppler_cooling)
        else:
            self.addSequence(doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(optical_pumping)
        self.addSequence(turn_off_all)
        self.addSequence(state_detection)
