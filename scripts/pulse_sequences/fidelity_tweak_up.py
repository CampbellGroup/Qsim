from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.Shelving import shelving
from sub_sequences.MLStateDetection import ml_state_detection
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.MicrowaveInterogation import microwave_interogation


class fidelity_tweak_up(pulse_sequence):

    required_subsequences = [shelving, shelving_doppler_cooling, doppler_cooling, standard_state_detection,shelving_state_detection, ml_state_detection, 
                             turn_off_all, bright_state_pumping, optical_pumping, microwave_interogation]

    required_parameters = [
                           ('BrightStatePumping', 'bright_prep_method'),('Modes', 'state_detection_mode'),
                           ]

    def sequence(self):

        bright_prep = self.parameters.BrightStatePumping.bright_prep_method
        mode = self.parameters.Modes.state_detection_mode

        self.addSequence(turn_off_all)

        if mode == 'Shelving':
            self.addSequence(shelving_doppler_cooling)
        else:
            self.addSequence(doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(bright_state_pumping)
        self.addSequence(turn_off_all)

        if mode == 'Standard':
            self.addSequence(standard_state_detection)
    
        elif mode == 'ML':
            self.addSequence(ml_state_detection)

        elif mode == 'Shelving':
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)

        self.addSequence(turn_off_all)

        if mode == 'Shelving':
            self.addSequence(shelving_doppler_cooling)
        else:
            self.addSequence(doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(optical_pumping)
        self.addSequence(turn_off_all)

        if mode == 'Standard':
            self.addSequence(standard_state_detection)
    
        elif mode == 'ML':
            self.addSequence(ml_state_detection)

        elif mode == 'Shelving':
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)

