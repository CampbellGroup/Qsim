from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Shelving import shelving
from sub_sequences.Deshelving import deshelving
from sub_sequences.MLStateDetection import ml_state_detection
from sub_sequences.ShelvingDopplerCooling import shelving_doppler_cooling


class ML_dark_state_preparation(pulse_sequence):

    required_subsequences = [shelving, turn_off_all, shelving_doppler_cooling, doppler_cooling, ml_state_detection, optical_pumping, deshelving]

    required_parameters = []

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(optical_pumping)

        self.addSequence(turn_off_all)
        self.addSequence(shelving)

        self.addSequence(turn_off_all)
        self.addSequence(ml_state_detection)

        self.addSequence(turn_off_all)
        self.addSequence(deshelving)
