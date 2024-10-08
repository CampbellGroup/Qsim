from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence
from labrad.units import WithUnit as U


class TestCameraDetection(PulseSequence):
    required_parameters = []

    def sequence(self):
        # simply trigger the camera for 10 ms of acquisition
        self.add_ttl("CameraTrigger", self.start, U(10.0, "ms"))

        self.end = self.start + U(10.0, "ms")
