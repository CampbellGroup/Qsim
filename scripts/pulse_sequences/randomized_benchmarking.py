from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.StandardStateDetection import standard_state_detection
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.RandomizedBenchmarking import randomized_benchmarking_pulse
from sub_sequences.microwave_pulse_sequences.MicrowaveSequenceStandard import microwave_sequence_standard
from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence


class randomized_benchmarking(pulse_sequence):

    required_subsequences = [doppler_cooling, standard_state_detection,
                             shelving_state_detection, turn_off_all,
                             shelving_doppler_cooling, shelving, deshelving,
                             optical_pumping, randomized_benchmarking_pulse,
                             microwave_sequence_standard]
    required_parameters = [
        ('Modes', 'state_detection_mode'),
    ]

    def sequence(self):
        mode = self.parameters.Modes.state_detection_mode

        # standard bright state is the 1 state
        if mode == 'Standard':
            self.addSequence(turn_off_all)
            self.addSequence(doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(randomized_benchmarking_pulse)
            self.addSequence(standard_state_detection)

        # shelving bright state is the 0 state
        elif mode == 'Shelving':
            self.addSequence(turn_off_all)
            self.addSequence(shelving_doppler_cooling)
            self.addSequence(optical_pumping)
            self.addSequence(randomized_benchmarking_pulse)
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelving)
