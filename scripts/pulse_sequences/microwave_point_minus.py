from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.microwave_pulse_sequences.MicrowaveInterrogationMinus import microwave_interrogation_minus
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.OpticalPumping import optical_pumping



class microwave_point_minus(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling,
                             microwave_interrogation_minus,
                             standard_state_detection,
                             optical_pumping]

    required_parameters = [
        ]

    def sequence(self):
        p = self.parameters

        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(microwave_interrogation_minus)
        self.addSequence(standard_state_detection)
