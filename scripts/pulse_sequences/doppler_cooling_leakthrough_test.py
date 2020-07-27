from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.Deshelving import deshelving
from sub_sequences.Shelving import shelving
from sub_sequences.DoublePass369 import double_pass_369

class doppler_cooling_leakthrough_test(pulse_sequence):

    required_subsequences = [doppler_cooling, standard_state_detection, optical_pumping,
                             doppler_cooling, shelving_state_detection, deshelving,
                             shelving, shelving_doppler_cooling, double_pass_369]

    required_parameters = [
        ('Modes', 'state_detection_mode'),
        ('EmptySequence', 'scan_empty_duration')
                           ]

    def sequence(self):
        p = self.parameters

        if p.Modes.state_detection_mode == 'Standard':
            self.addSequence(doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(double_pass_369)
            self.addSequence(standard_state_detection)

        elif p.Modes.state_detection_mode == 'Shelving':
            self.addSequence(shelving_doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(double_pass_369)
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelving)
