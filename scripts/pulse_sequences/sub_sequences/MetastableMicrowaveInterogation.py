from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import numpy as np


class metastable_microwave_interogation(pulse_sequence):

    required_parameters = [
                           ('MetastableMicrowaveInterogation', 'duration'),
                           ('MetastableMicrowaveInterogation', 'detuning'),
                           ('MetastableMicrowaveInterogation', 'power'),
                           ('MetastableMicrowaveInterogation', 'deshelving_time'),
                           ('Transitions', 'MetastableQubit'),
                           ('Transitions', 'qubit_plus'),
                           ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.MetastableQubit
        DDS_freq = U(270.000, 'MHz') - (p.MetastableMicrowaveInterogation.detuning + center)

        self.addDDS('3GHz_qubit',
                    self.start,
                    p.MetastableMicrowaveInterogation.duration,
                    DDS_freq,
                    p.MetastableMicrowaveInterogation.power)

        # turning on the 760 after microwacve interrogation for now because we dont
        # know what the Pi time is, so we just leave on the microwaves for a while and
        # deshelve whatever gets moved to the F = 4 manifold
        self.addDDS('760SP2',
                    self.start + p.MetastableMicrowaveInterogation.duration,
                    p.MetastableMicrowaveInterogation.deshelving_time,
                    U(160.0, 'MHz'),
                    U(6.0, 'dBm'))

        self.end = self.start + p.MetastableMicrowaveInterogation.duration + p.MetastableMicrowaveInterogation.deshelving_time
