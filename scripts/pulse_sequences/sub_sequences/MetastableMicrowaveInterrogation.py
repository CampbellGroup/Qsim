from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U


class metastable_microwave_interrogation(pulse_sequence):

    required_parameters = [
        ('MetastableMicrowaveInterrogation', 'duration'),
        ('MetastableMicrowaveInterrogation', 'detuning'),
        ('MetastableMicrowaveInterrogation', 'power'),
        ('MetastableMicrowaveInterrogation', 'deshelving_time'),
        ('Transitions', 'MetastableQubit'),
        ('Transitions', 'qubit_plus'),
        ('ddsDefaults', 'repump_760_2_freq'),
        ('ddsDefaults', 'repump_760_2_power'),
    ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.MetastableQubit
        DDS_freq = U(270.000, 'MHz') - (p.MetastableMicrowaveInterrogation.detuning + center)

        self.addDDS('3GHz_qubit',
                    self.start,
                    p.MetastableMicrowaveInterrogation.duration,
                    DDS_freq,
                    p.MetastableMicrowaveInterrogation.power)

        # turning on the 760 after microwave interrogation for now because we dont
        # know what the Pi time is, so we just leave on the microwaves for a while and
        # deshelve whatever gets moved to the F = 4 manifold
        self.addDDS('760SP2',
                    self.start + p.MetastableMicrowaveInterrogation.duration,
                    p.MetastableMicrowaveInterrogation.deshelving_time,
                    p.ddsDefaults.repump_760_2_freq,
                    p.ddsDefaults.repump_760_2_power)

        self.end = self.start + p.MetastableMicrowaveInterrogation.duration + p.MetastableMicrowaveInterrogation.deshelving_time