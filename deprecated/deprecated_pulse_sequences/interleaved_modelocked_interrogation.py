from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.ML_interogation import ML_interogation


class interleaved_modelocked_interrogation(pulse_sequence):

    required_subsequences = [turn_off_all, ML_interogation, doppler_cooling]

    def sequence(self):
        self.addSequence(turn_off_all)
        self.addSequence(doppler_cooling)

        self.addSequence(turn_off_all)
        self.addSequence(ML_interogation)
