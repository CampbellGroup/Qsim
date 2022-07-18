from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import doppler_cooling
from sub_sequences.turn_off_all import turn_off_all
from sub_sequences.optical_pumping import optical_pumping
from sub_sequences.state_detection.standard_state_detection import standard_state_detection
from sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interrogation
from BrightStatePumping import bright_state_pumping
from sub_sequences.shelving import shelving
from sub_sequences.deshelving import deshelving


class dark_state_preparation(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling, standard_state_detection,
                             shelving_state_detection, optical_pumping, shelving, shelving_doppler_cooling,
                             deshelving, bright_state_pumping, microwave_interrogation]

    required_parameters = [
        ('Modes', 'state_detection_mode'),
        ('BrightStatePumping', 'start_with_Hadamard')]

    def sequence(self):

        mode = self.parameters.Modes.state_detection_mode

        # standard dark state is the |0> state
        if mode == 'Standard':
            self.addSequence(doppler_cooling)
            self.addSequence(optical_pumping)
            if self.parameters.BrightStatePumping.start_with_Hadamard == 'On':
                self.addSequence(bright_state_pumping)
            self.addSequence(standard_state_detection)

        # shelving dark state is the |1> state
        elif mode == 'Shelving':
            self.addSequence(turn_off_all)
            self.addSequence(shelving_doppler_cooling)
            self.addSequence(bright_state_pumping)
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelving)
