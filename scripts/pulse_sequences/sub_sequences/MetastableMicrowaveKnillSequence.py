from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class metastable_microwave_knill_sequence(pulse_sequence):

    required_parameters = [
        ('Metastable_Microwave_Interrogation', 'duration'),
        ('Metastable_Microwave_Interrogation', 'detuning'),
        ('Metastable_Microwave_Interrogation', 'power'),
        ('Transitions', 'MetastableQubit'),
        ('ddsDefaults', 'metastable_qubit_dds_freq'),
        ('ddsDefaults', 'metastable_qubit_dds_power'),
    ]

    def sequence(self):
        p = self.parameters
        center = p.Transitions.MetastableQubit
        DDS_freq = p.ddsDefaults.metastable_qubit_dds_freq - (p.MetastableMicrowaveInterrogation.detuning + center)

        self.addDDS('3GHz_qubit',
                    self.start,
                    p.MetastableMicrowaveInterrogation.duration,
                    DDS_freq,
                    p.ddsDefaults.metastable_qubit_dds_power,
                    U(30.0, 'deg'))

        self.addDDS('3GHz_qubit',
                    self.start + p.MetastableMicrowaveInterrogation.duration,
                    p.MetastableMicrowaveInterrogation.duration,
                    DDS_freq,
                    p.ddsDefaults.metastable_qubit_dds_power,
                    U(0.0, 'deg'))

        self.addDDS('3GHz_qubit',
                    self.start + 2*p.MetastableMicrowaveInterrogation.duration,
                    p.MetastableMicrowaveInterrogation.duration,
                    DDS_freq,
                    p.ddsDefaults.metastable_qubit_dds_power,
                    U(90.0, 'deg'))

        self.addDDS('3GHz_qubit',
                    self.start + 3*p.MetastableMicrowaveInterrogation.duration,
                    p.MetastableMicrowaveInterrogation.duration,
                    DDS_freq,
                    p.ddsDefaults.metastable_qubit_dds_power,
                    U(0.0, 'deg'))

        self.addDDS('3GHz_qubit',
                    self.start + 4*p.MetastableMicrowaveInterrogation.duration,
                    p.MetastableMicrowaveInterrogation.duration,
                    DDS_freq,
                    p.ddsDefaults.metastable_qubit_dds_power,
                    U(30.0, 'deg'))

        self.end = self.start + 5*p.MetastableMicrowaveInterrogation.duration
