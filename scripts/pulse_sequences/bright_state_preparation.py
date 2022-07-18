from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import doppler_cooling
from sub_sequences.state_detection.standard_state_detection import standard_state_detection
from sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from sub_sequences.turn_off_all import turn_off_all
from BrightStatePumping import bright_state_pumping
from sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from sub_sequences.shelving import shelving
from sub_sequences.deshelving import deshelving
from sub_sequences.optical_pumping import optical_pumping
from sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interrogation


class bright_state_preparation(pulse_sequence):

    required_subsequences = [doppler_cooling, standard_state_detection,
                             shelving_state_detection, turn_off_all, bright_state_pumping,
                             shelving_doppler_cooling, shelving, deshelving, optical_pumping,
                             microwave_interrogation]
    required_parameters = [
        ('Modes', 'state_detection_mode')]

    def sequence(self):

        mode = self.parameters.Modes.state_detection_mode

        # standard bright state is the 1 state
        if mode == 'Standard':
            self.addSequence(turn_off_all)
            self.addSequence(doppler_cooling)
            self.addSequence(bright_state_pumping)
            self.addSequence(standard_state_detection)

        # shelving bright state is the 0 state
        elif mode == 'Shelving':
            self.addSequence(turn_off_all)
            self.addSequence(shelving_doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelving)
