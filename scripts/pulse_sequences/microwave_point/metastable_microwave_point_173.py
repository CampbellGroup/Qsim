from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interrogation
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.metastable_microwave_interrogation_173 import \
    metastable_microwave_interrogation_173, swept_metastable_microwave_interrogation_173
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import turn_off_all
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.metastable_state_detection_173 import metastable_state_detection_173
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import optical_pumping
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_173 import shelving_173
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import deshelving


class metastable_microwave_point_173(pulse_sequence):

    required_subsequences = [turn_off_all, metastable_microwave_interrogation_173,
                             metastable_state_detection_173, optical_pumping, shelving_173,
                             shelving_doppler_cooling, deshelving, microwave_interrogation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(shelving_173)
        self.addSequence(metastable_microwave_interrogation_173)
        self.addSequence(metastable_state_detection_173)
        self.addSequence(deshelving)


class swept_metastable_microwave_point_173(pulse_sequence):

    required_subsequences = [turn_off_all, swept_metastable_microwave_interrogation_173,
                             metastable_state_detection_173, optical_pumping, shelving_173,
                             shelving_doppler_cooling, deshelving, microwave_interrogation]

    required_parameters = [
        ]

    def sequence(self):

        self.addSequence(turn_off_all)
        self.addSequence(shelving_doppler_cooling)
        self.addSequence(shelving_173)
        self.addSequence(swept_metastable_microwave_interrogation_173)
        self.addSequence(metastable_state_detection_173)
        self.addSequence(deshelving)
