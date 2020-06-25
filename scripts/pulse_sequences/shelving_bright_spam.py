from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.ShelvingStateDetection import shelving_state_detection
from sub_sequences.Shelving import shelving
from sub_sequences.OpticalPumping import optical_pumping
from sub_sequences.Deshelving import deshelving


class shelving_bright_spam(pulse_sequence):
    required_subsequences = [shelving, doppler_cooling, shelving_state_detection, deshelving,
                             optical_pumping]

    required_parameters = [
    ]

    def sequence(self):
        self.addSequence(doppler_cooling)
        self.addSeqeucne(optical_pumping)
        self.addSequence(shelving)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving)
