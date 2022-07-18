from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from sub_sequences.shelving import Shelving
from sub_sequences.deshelving import Deshelving
from sub_sequences.variable_deshelving import VariableDeshelving
from sub_sequences.turn_off_all import TurnOffAll


class deshelving_point(pulse_sequence):

    required_subsequences = [TurnOffAll, ShelvingDopplerCooling, Shelving,
                             Deshelving, VariableDeshelving, ShelvingStateDetection]

    def sequence(self):
        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)
        self.addSequence(Shelving)
        self.addSequence(VariableDeshelving)  # scannable duration hacks since cant replace parameter for just one
        self.addSequence(ShelvingStateDetection)
        self.addSequence(Deshelving)
