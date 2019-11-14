from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.MicrowaveInterogation import microwave_interogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.MLStateDetection import ml_state_detection
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.EmptySequence import empty_sequence
from sub_sequences.Shelving import shelving


class microwave_ramsey_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling, shelving_doppler_cooling,
                             microwave_interogation, shelving_state_detection, ml_state_detection,
                             standard_state_detection, optical_pumping, empty_sequence, shelving]

    required_parameters = [
                          ('Modes', 'state_detection_mode')
        ]

    def sequence(self):
        mode = self.parameters.Modes.state_detection_mode
        self.addSequence(turn_off_all)
        if mode == 'Shelving':
            self.addSequence(shelving_doppler_cooling)
        else:
            self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(microwave_interogation)
        self.addSequence(empty_sequence)
        self.addSequence(microwave_interogation)
        if mode == 'Shelving':
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)
        elif mode == 'Standard':
            self.addSequence(standard_state_detection)
        elif mode == 'ML':
            self.addSequence(ml_state_detection)
