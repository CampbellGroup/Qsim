from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class pulser_phase_diagnostic(pulse_sequence):

    required_parameters = [
                           ]

    def sequence(self):
        p = self.parameters
        duration = U(100.0, 'us')
        f1 = U(100.0, 'MHz')
        f2 = U(120.0, 'MHz')
        interrupt_duration = 0.33*duration
        interrupt_time = 0.33*duration

        #start
        self.addDDS('760SP',
                    start=self.start,
                    duration=interrupt_time,
                    frequency=f1,
                    amplitude=U(-5, 'dBm'))

        #switch frequency at some time
        self.addDDS('760SP',
                    start=self.start + interrupt_time,
                    duration=interrupt_duration,
                    frequency=f2,
                    amplitude=U(-5, 'dBm'))

        #switch back at a later time
        self.addDDS('760SP',
                    start=self.start + interrupt_time + interrupt_duration,
                    duration=duration-interrupt_duration-interrupt_time,
                    frequency=f1,
                    amplitude=U(-5, 'dBm'))

        #reference frequency never changes
        self.addDDS('3_GHz_qubit',
                    start=self.start,
                    duration=duration,
                    frequency=f1,
                    amplitude=U(-5, 'dBm'))

        self.end = self.start + duration
