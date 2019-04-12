from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U

class microwave_interogation(pulse_sequence):

    required_parameters = [
                           ('MicrowaveInterogation', 'duration'),
                           ('MicrowaveInterogation', 'detuning'),
                           ('MicrowaveInterogation', 'power'),
                           ('MicrowaveInterogation', 'knill_sequence'),
                           ('Line_Selection', 'qubit'),
                           ('Transitions', 'qubit_0'),
                           ('Transitions', 'qubit_plus'),
                           ('Transitions', 'qubit_minus')
                           ]

    def sequence(self):
        p = self.parameters
        
        #select which zeeman level to prepare
        if p.Line_Selection.qubit == 'qubit_0':
            center = p.Transitions.qubit_0

        elif p.Line_Selection.qubit == 'qubit_plus':
            center = p.Transitions.qubit_plus

        elif p.Line_Selection.qubit == 'qubit_minus':
            center = p.Transitions.qubit_minus

        DDS_freq = U(197.188, 'MHz') - (p.MicrowaveInterogation.detuning + center)

        #decide if you want to use the Knill sequence or just standard microwave interrogation
        if p.MicrowaveInterogation.knill_sequence == 'off':
            self.addDDS('Microwave_qubit',
                        self.start,
                        p.MicrowaveInterogation.duration,
                        DDS_freq,
                        p.MicrowaveInterogation.power)
            self.end = self.start + p.MicrowaveInterogation.duration
            
        elif p.MicrowaveInterogation.knill_sequence == 'on':
            self.addDDS('Microwave_qubit',
                        self.start,
                        p.MicrowaveInterogation.duration,
                        DDS_freq,
                        p.MicrowaveInterogation.power,
                        U(30.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + p.MicrowaveInterogation.duration,
                        p.MicrowaveInterogation.duration,
                        DDS_freq,
                        p.MicrowaveInterogation.power,
                        U(0.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 2*p.MicrowaveInterogation.duration,
                        p.MicrowaveInterogation.duration,
                        DDS_freq,
                        p.MicrowaveInterogation.power,
                        U(90.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 3*p.MicrowaveInterogation.duration,
                        p.MicrowaveInterogation.duration,
                        DDS_freq,
                        p.MicrowaveInterogation.power,
                        U(0.0, 'deg'))
            self.addDDS('Microwave_qubit',
                        self.start + 4*p.MicrowaveInterogation.duration,
                        p.MicrowaveInterogation.duration,
                        DDS_freq,
                        p.MicrowaveInterogation.power,
                        U(30.0, 'deg'))
            self.end = self.start + 5*p.MicrowaveInterogation.duration
