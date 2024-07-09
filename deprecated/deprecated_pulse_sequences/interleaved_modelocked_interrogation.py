from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from sub_sequences.DopplerCooling import doppler_cooling
from sub_sequences.TurnOffAll import turn_off_all
from sub_sequences.ML_interogation import ML_interogation


class interleaved_modelocked_interrogation(PulseSequence):

    required_subsequences = [turn_off_all, ML_interogation, doppler_cooling]

    def sequence(self):
        self.add_sequence(turn_off_all)
        self.add_sequence(doppler_cooling)

        self.add_sequence(turn_off_all)
        self.add_sequence(ML_interogation)
