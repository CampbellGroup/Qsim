from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling
from sub_sequences.MLStateDetection import ml_state_detection
from sub_sequences.Shelving import shelving
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.Deshelving import deshelving
from sub_sequences.BrightStatePumping import bright_state_pumping
from sub_sequences.DopplerCooling import doppler_cooling


class ML_bright_state_preparation(PulseSequence):

    required_subsequences = [
        doppler_cooling,
        shelving,
        shelving_doppler_cooling,
        ml_state_detection,
        turn_off_all,
        bright_state_pumping,
        deshelving,
    ]
    required_parameters = []

    def sequence(self):

        self.add_sequence(turn_off_all)
        self.add_sequence(shelving_doppler_cooling)

        self.add_sequence(turn_off_all)
        self.add_sequence(bright_state_pumping)

        self.add_sequence(turn_off_all)
        self.add_sequence(shelving)

        self.add_sequence(turn_off_all)
        self.add_sequence(ml_state_detection)

        self.add_sequence(turn_off_all)
        self.add_sequence(deshelving)
        # self.addSequence(shelving_state_detection)
