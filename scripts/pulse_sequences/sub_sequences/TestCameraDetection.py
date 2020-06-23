from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class test_camera_detection(pulse_sequence):

    required_parameters = [
    ]

    def sequence(self):
        # simply trigger the camera for 10 ms of acquisition
       self.addTTL('CameraTrigger',
                   self.start,
                   U(10.0, 'ms'))

       self.end = self.start + U(10.0, 'ms')
