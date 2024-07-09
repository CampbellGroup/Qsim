from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.ML_interogation import ML_interogation
from sub_sequences.MicrowaveInterogation import microwave_interogation
from sub_sequences.MicrowaveInterrogationMinus import microwave_interogation_minus


class ML_decoherence(PulseSequence):

    required_subsequences = [doppler_cooling, standard_state_detection,
                             turn_off_all, bright_state_pumping, optical_pumping, ML_interogation,
                             microwave_interogation, microwave_interogation_minus]

    required_parameters = [('ML_decoherence', 'additional_pi_pulse'), ('Line_Selection','qubit')]

    def sequence(self):
        pi_pulse = self.parameters.ML_decoherence.additional_pi_pulse
        self.add_sequence(turn_off_all)
        self.add_sequence(doppler_cooling)
        self.add_sequence(bright_state_pumping)
        self.add_sequence(ML_interogation)
        if pi_pulse == 'ON':
            self.add_sequence(microwave_interogation)
        self.add_sequence(standard_state_detection)

        self.add_sequence(doppler_cooling)
        self.add_sequence(optical_pumping)
        self.add_sequence(ML_interogation)
        if pi_pulse == 'ON':
            self.add_sequence(microwave_interogation)
        self.add_sequence(standard_state_detection)
