from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.TurnOffAll import turn_off_all
from BrightStatePumping import bright_state_pumping
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.MicrowaveInterrogation import microwave_interrogation


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

