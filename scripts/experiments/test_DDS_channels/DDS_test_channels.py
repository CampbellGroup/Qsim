import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment


class DDS_test_channels(QsimExperiment):

    name = 'DDS channel tester'

    exp_parameters = []
    exp_parameters.append(('testDDS', 'channel'))
    exp_parameters.append(('testDDS', 'duration'))
    exp_parameters.append(('testDDS', 'frequency'))
    exp_parameters.append(('testDDS', 'power'))
    exp_parameters.append(('testDDS', 'phase'))
    exp_parameters.append(('testDDS', 'ramprate'))
    exp_parameters.append(('testDDS', 'ampramprate'))
    exp_parameters.append(('testDDS', 'cycles'))

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
        self.chan = self.p.testDDS.channel
        self.duration = self.p.testDDS.duration
        self.pulser.new_sequence()

        self.pulser.add_dds_pulses([(self.chan, self.starttime,
                                     self.duration,
                                     self.p.testDDS.frequency,
                                     self.U(-48.0, 'dBm'),
                                     self.p.testDDS.phase,
                                     self.p.testDDS.ramprate,
                                     self.p.testDDS.ampramprate)])

        self.pulser.add_dds_pulses([(self.chan,
                                     self.starttime + self.duration,
                                     self.duration,
                                     self.p.testDDS.frequency,
                                     self.p.testDDS.power,
                                     self.p.testDDS.phase,
                                     self.p.testDDS.ramprate,
                                     self.p.testDDS.ampramprate)])

        self.pulser.add_dds_pulses([(self.chan,
                                     self.starttime + 2*self.duration,
                                     self.duration,
                                     self.p.testDDS.frequency,
                                     self.U(-48.0, 'dBm'),
                                     self.p.testDDS.phase,
                                     self.p.testDDS.ramprate,
                                     self.p.testDDS.ampramprate)])

        self.pulser.program_sequence()
        self.pulser.start_number(int(self.p.testDDS.cycles))

    def finalize(self, cxn, context):
        self.pulser.stop_sequence()

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DDS_test_channels(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




