from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling import doppler_cooling
from Qsim.scripts.pulse_sequences.sub_sequences.doppler_cooling_fiber_eom import doppler_cooling_fiber_eom
from Qsim.scripts.pulse_sequences.sub_sequences.microwave_interrogation.microwave_interrogation import microwave_interrogation
from Qsim.scripts.pulse_sequences.sub_sequences.turn_off_all import turn_off_all
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection import standard_state_detection
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.standard_state_detection_fiber_eom import standard_state_detection_fiber_eom
from Qsim.scripts.pulse_sequences.sub_sequences.state_detection.shelving_state_detection import shelving_state_detection
from Qsim.scripts.pulse_sequences.sub_sequences.shelving_doppler_cooling import shelving_doppler_cooling
from Qsim.scripts.pulse_sequences.sub_sequences.optical_pumping import optical_pumping
from Qsim.scripts.pulse_sequences.sub_sequences.shelving import shelving
from Qsim.scripts.pulse_sequences.sub_sequences.deshelving import deshelving


class microwave_point(pulse_sequence):

    required_subsequences = [turn_off_all, doppler_cooling,
                             microwave_interrogation,
                             standard_state_detection, shelving_state_detection, deshelving,
                             optical_pumping, shelving, shelving_doppler_cooling, doppler_cooling_fiber_eom,
                             standard_state_detection_fiber_eom]

    required_parameters = [
        ('Modes', 'state_detection_mode'),
        ('MicrowaveInterrogation', 'repetitions')
        ]

    def sequence(self):
        p = self.parameters
        mode = p.Modes.state_detection_mode

        self.addSequence(turn_off_all)

        if mode == 'Standard' or mode == 'StandardFiberEOM':
            self.addSequence(doppler_cooling)
            self.addSequence(optical_pumping)
            for i in range(int(p.MicrowaveInterrogation.repetitions)):
                self.addSequence(microwave_interrogation)
            self.addSequence(standard_state_detection)

        elif mode == 'Shelving':
            self.addSequence(shelving_doppler_cooling)
            self.addSequence(optical_pumping)
            for i in range(int(p.MicrowaveInterrogation.repetitions)):
                self.addSequence(microwave_interrogation)
            self.addSequence(shelving)
            self.addSequence(shelving_state_detection)
            self.addSequence(deshelving)
