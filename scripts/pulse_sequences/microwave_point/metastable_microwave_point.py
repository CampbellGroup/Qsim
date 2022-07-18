from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interrogation
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.metastable_microwave_interrogation import metastable_microwave_interrogation
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import turn_off_all
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.metastable_state_detection import metastable_state_detection
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import optical_pumping
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import deshelving


class metastable_microwave_point(pulse_sequence):

    required_subsequences = [turn_off_all, metastable_microwave_interrogation,
                             metastable_state_detection, optical_pumping, shelving,
                             shelving_doppler_cooling, deshelving, microwave_interrogation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(optical_pumping)
        # self.addSequence(microwave_interrogation)
        self.addSequence(shelving)
        self.addSequence(metastable_microwave_interrogation)
        self.addSequence(metastable_state_detection)
        self.addSequence(deshelving)
