from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling import doppler_cooling
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_pulse_sequences.microwave_interrogation_plus import microwave_interrogation_plus
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import turn_off_all
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import standard_state_detection
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import optical_pumping


class microwave_point_plus(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling,
                             microwave_interrogation_plus,
                             standard_state_detection,
                             optical_pumping]

    required_parameters = [
        ]

    def sequence(self):
        p = self.parameters

        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(microwave_interrogation_plus)
        self.addSequence(standard_state_detection)
