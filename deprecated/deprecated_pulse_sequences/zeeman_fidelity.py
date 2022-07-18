from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from scripts.pulse_sequences.sub_sequences.quadrupole_interrogation import quadrupole_interogation
from scripts.pulse_sequences.sub_sequences.turn_off_all import TurnOffAll
from scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import ShelvingStateDetection
from scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import ShelvingDopplerCooling
from deprecated.deprecated_sub_sequences.ZeemanOpticalPumping import zeeman_bright_optical_pumping
from deprecated.deprecated_sub_sequences.ZeemanOpticalPumping import zeeman_dark_optical_pumping
from scripts.pulse_sequences.sub_sequences.shelving import Shelving
from scripts.pulse_sequences.sub_sequences.deshelving import Deshelving


class zeeman_fidelity(pulse_sequence):

    required_subsequences = [TurnOffAll, quadrupole_interogation, ShelvingStateDetection,
                             Shelving, ShelvingDopplerCooling, Deshelving,
                             zeeman_bright_optical_pumping, zeeman_dark_optical_pumping]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(TurnOffAll)
        self.addSequence(ShelvingDopplerCooling)
        self.addSequence(zeeman_bright_optical_pumping)
        self.addSequence(Shelving)
        self.addSequence(ShelvingStateDetection)
        self.addSequence(Deshelving)

        self.addSequence(ShelvingDopplerCooling)
        self.addSequence(zeeman_dark_optical_pumping)
        self.addSequence(Shelving)
        self.addSequence(ShelvingStateDetection)
        self.addSequence(Deshelving)
