from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling import doppler_cooling
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import turn_off_all
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import standard_state_detection
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import optical_pumping
from Qsim.scripts.pulse_sequences.sub_sequences.empty_sequence import empty_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import deshelving
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.ramsey_microwave_interrogation import ramsey_microwave_interrogation


class microwave_ramsey_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling,
                             shelving_state_detection,
                             deshelving, standard_state_detection,
                             optical_pumping, empty_sequence, shelving,
                             ramsey_microwave_interrogation, shelving_doppler_cooling]

    required_parameters = [
                          ('Modes', 'state_detection_mode')
        ]

    def sequence(self):
        mode = self.parameters.Modes.state_detection_mode

        if mode == 'Shelving':
            self.addSequence(turn_off_all)
            self.addSequence(shelving_doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(ramsey_microwave_interrogation)
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelving)
        elif mode == 'Standard':
            self.addSequence(turn_off_all)
            self.addSequence(doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(ramsey_microwave_interrogation)
            self.addSequence(standard_state_detection)
