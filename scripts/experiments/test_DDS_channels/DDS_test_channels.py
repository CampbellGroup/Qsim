import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment


class DDS_test_channels(QsimExperiment):

    name = 'DDS channel tester'

    exp_parameters = []
#    exp_parameters.append(('testDDS', 'channel'))
#    exp_parameters.append(('testDDS', 'duration'))
#    exp_parameters.append(('testDDS', 'frequency'))
#    exp_parameters.append(('testDDS', 'power'))
#    exp_parameters.append(('testDDS', 'phase'))
#    exp_parameters.append(('testDDS', 'ramprate'))
#    exp_parameters.append(('testDDS', 'ampramprate'))
#    exp_parameters.append(('testDDS', 'cycles'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        from labrad.units import WithUnit as U
        self.U = U
        self.pulser = self.cxn.pulser
        self.starttime = self.U(0.001, 's')

    def run(self, cxn, context):

        '''
        This experiment turns the selected DDS's off for a duration, then
        sets them to the given parameters for that duration then off for
        the same duration
        '''
        self.chan = 'Microwave_qubit'
        self.chan2 = '369DP'
        self.duration = self.U(10, 'us')
        self.pulser.new_sequence()

        self.pulser.add_dds_pulses([(self.chan2, self.starttime,
                                     3*self.duration,
                                     self.U(200.0, 'MHz'),
                                     self.U(-7.0, 'dBm'),
                                     self.U(0.0, 'deg'),
                                     self.U(0.0, 'MHz'),
                                     self.U(0.0, 'dB'))])
        
        self.pulser.add_dds_pulses([(self.chan, self.starttime,
                                     self.duration,
                                     self.U(2.0, 'MHz'),
                                     self.U(-7.0, 'dBm'),
                                     self.U(23.0, 'deg'),
                                     self.U(0.0, 'MHz'),
                                     self.U(0.0, 'dB'))])

        self.pulser.add_dds_pulses([(self.chan, self.starttime + self.duration,
                                     self.duration,
                                     self.U(2.0, 'MHz'),
                                     self.U(-7.0, 'dBm'),
                                     self.U(112.0, 'deg'),
                                     self.U(0.0, 'MHz'),
                                     self.U(0.0, 'dB'))])

        self.pulser.add_dds_pulses([(self.chan, self.starttime + 2*self.duration,
                                     self.duration,
                                     self.U(2.0, 'MHz'),
                                     self.U(-7.0, 'dBm'),
                                     self.U(23.0, 'deg'),
                                     self.U(0.0, 'MHz'),
                                     self.U(0.0, 'dB'))])
         

        self.pulser.program_sequence()
        self.pulser.start_number(10)

    def finalize(self, cxn, context):
        self.pulser.stop_sequence()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DDS_test_channels(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




