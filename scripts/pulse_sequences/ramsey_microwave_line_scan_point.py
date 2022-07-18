from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import doppler_cooling
from sub_sequences.turn_off_all import turn_off_all
from sub_sequences.microwave_interrogation.ramsey_microwave_interrogation import ramsey_microwave_interrogation
from sub_sequences.state_detection.standard_state_detection import standard_state_detection
from sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from sub_sequences.optical_pumping import optical_pumping
from sub_sequences.shelving import shelving
from sub_sequences.deshelving import deshelving


class ramsey_microwave_line_scan_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling,
                             ramsey_microwave_interrogation,
                             standard_state_detection, shelving_state_detection, deshelving,
                             optical_pumping, shelving, shelving_doppler_cooling]

    required_parameters = [
        ('Modes', 'state_detection_mode'),
        ('MicrowaveInterrogation', 'repetitions')
        ]

    def sequence(self):
        p = self.parameters
        mode = p.Modes.state_detection_mode

        self.addSequence(turn_off_all)

        if mode == 'Standard':
            self.addSequence(doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(ramsey_microwave_interrogation)
            self.addSequence(standard_state_detection)

        elif mode == 'Shelving':
            self.addSequence(shelving_doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(ramsey_microwave_interrogation)
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelving)
