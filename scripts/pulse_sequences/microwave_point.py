from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.MicrowaveInterogation import microwave_interogation
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving


class microwave_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling,
                             microwave_interogation,
                             standard_state_detection, shelving_state_detection, deshelving,
                             optical_pumping, shelving, shelving_doppler_cooling]

    required_parameters = [
        ('Modes', 'state_detection_mode'),
        ('MicrowaveInterogation', 'repititions')
        ]

    def sequence(self):
        p = self.parameters
        mode = p.Modes.state_detection_mode

        self.addSequence(turn_off_all)

        if mode == 'Shelving':
            self.addSequence(shelving_doppler_cooling)
            self.addSequence(optical_pumping)
        else:
            self.addSequence(doppler_cooling)
            self.addSequence(optical_pumping)

        for i in range(int(p.MicrowaveInterogation.repititions)):
            self.addSequence(microwave_interogation)

        if mode == 'Shelving':
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelving)
        elif mode == 'Standard':
            self.addSequence(standard_state_detection)
