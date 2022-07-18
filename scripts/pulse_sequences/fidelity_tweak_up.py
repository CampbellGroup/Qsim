from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.doppler_cooling import doppler_cooling
from sub_sequences.state_detection.standard_state_detection import standard_state_detection
from sub_sequences.turn_off_all import turn_off_all
from sub_sequences.optical_pumping import optical_pumping
from sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interrogation
from BrightStatePumping import bright_state_pumping


class fidelity_tweak_up(pulse_sequence):
    required_subsequences = [doppler_cooling, standard_state_detection, turn_off_all,
                             bright_state_pumping, optical_pumping, microwave_interrogation]

    required_parameters = [
    ]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(bright_state_pumping)
        self.addSequence(standard_state_detection)

        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(standard_state_detection)
