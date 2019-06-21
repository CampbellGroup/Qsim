from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.MLStateDetection import ml_state_detection
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.BrightStatePumping import bright_state_pumping


class bright_state_preperation(pulse_sequence):

    required_subsequences = [doppler_cooling, standard_state_detection, ml_state_detection,
                             shelving_state_detection, turn_off_all, bright_state_pumping]
    required_parameters = [
        ('Modes', 'state_detection_mode')]

    def sequence(self):

        mode = self.parameters.Modes.state_detection_mode

        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(bright_state_pumping)

        self.addSequence(turn_off_all)
        if mode == 'Standard':
            self.addSequence(standard_state_detection)
        elif mode == 'Shelving':
            self.addSequence(shelving_state_detection)
