from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.ML_interogation import ML_interogation
from sub_sequences.MicrowaveInterogation import microwave_interogation
from sub_sequences.MicrowaveInterrogationMinus import microwave_interogation_minus


class ML_decoherence(pulse_sequence):

    required_subsequences = [doppler_cooling, standard_state_detection,
                             turn_off_all, bright_state_pumping, optical_pumping, ML_interogation,
                             microwave_interogation, microwave_interogation_minus]

    required_parameters = [('ML_decoherence', 'additional_pi_pulse'), ('Line_Selection','qubit')]

    def sequence(self):
        pi_pulse = self.parameters.ML_decoherence.additional_pi_pulse
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)
        self.addSequence(bright_state_pumping)
        self.addSequence(ML_interogation)
        if pi_pulse == 'ON':
            self.addSequence(microwave_interogation)
        self.addSequence(standard_state_detection)

        self.addSequence(doppler_cooling)
        self.addSequence(optical_pumping)
        self.addSequence(ML_interogation)
        if pi_pulse == 'ON':
            self.addSequence(microwave_interogation)
        self.addSequence(standard_state_detection)
