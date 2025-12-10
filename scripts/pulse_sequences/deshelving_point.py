from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from .sub_sequences.state_detection.shelving_state_detection import (
    ShelvingStateDetection,
)
from .sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from .sub_sequences.shelving import Shelving
from .sub_sequences.deshelving import Deshelving
from .sub_sequences.variable_deshelving import VariableDeshelving
from .sub_sequences.turn_off_all import TurnOffAll
from .sub_sequences.bright_state_pumping import BrightStatePumping


class DeshelvingPoint(PulseSequence):
    required_subsequences = [
        TurnOffAll,
        ShelvingDopplerCooling,
        Shelving,
        Deshelving,
        VariableDeshelving,
        ShelvingStateDetection,
        BrightStatePumping,
    ]

    def sequence(self):
        self.add_sequence(TurnOffAll)
        self.add_sequence(ShelvingDopplerCooling)
        ## 4/3/25 Drew ##
        self.add_sequence(TurnOffAll)
        self.add_sequence(BrightStatePumping)
        ### for dark state prep ###
        self.add_sequence(Shelving)
        self.add_sequence(
            VariableDeshelving
        )  # scannable duration hacks since cant replace parameter for just one
        self.add_sequence(ShelvingStateDetection)
        self.add_sequence(Deshelving)
