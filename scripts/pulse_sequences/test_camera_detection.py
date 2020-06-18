from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from sub_sequences.TestCameraDetection import test_camera_detection


class test_camera_detection(pulse_sequence):
    required_subsequences = [test_camera_detection]

    def sequence(self):
        self.addSequence(test_camera_detection)
