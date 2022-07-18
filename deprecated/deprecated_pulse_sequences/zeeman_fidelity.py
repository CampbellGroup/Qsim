from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from scripts.pulse_sequences.sub_sequences.quadrupole_interrogation import quadrupole_interogation
from scripts.pulse_sequences.sub_sequences.turn_off_all import turn_off_all
from scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from deprecated.deprecated_sub_sequences.ZeemanOpticalPumping import zeeman_bright_optical_pumping
from deprecated.deprecated_sub_sequences.ZeemanOpticalPumping import zeeman_dark_optical_pumping
from scripts.pulse_sequences.sub_sequences.shelving import shelving
from scripts.pulse_sequences.sub_sequences.deshelving import deshelving


class zeeman_fidelity(pulse_sequence):

    required_subsequences = [turn_off_all, quadrupole_interogation, shelving_state_detection,
                             shelving, shelving_doppler_cooling, deshelving,
                             zeeman_bright_optical_pumping, zeeman_dark_optical_pumping]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(zeeman_bright_optical_pumping)
        self.addSequence(shelving)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving)

        self.addSequence(shelving_doppler_cooling)
        self.addSequence(zeeman_dark_optical_pumping)
        self.addSequence(shelving)
        self.addSequence(shelving_state_detection)
        self.addSequence(deshelving)
