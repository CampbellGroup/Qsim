import labrad
import numpy as np
from common.lib.servers.script_scanner.scan_methods import experiment
from Qsim.scripts.pulse_sequences.sub_sequences.RecordTimeTags import record_timetags
from treedict import TreeDict


class TD_flourescence(experiment):

    name = 'TD Flourescence'

    exp_parameters = []
    exp_parameters.append(('TrapFrequencies', 'rf_drive_frequency'))
    exp_parameters.append(('TD_Flourescence', 'record_time'))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.record_time = self.parameters.TD_Flourescence.record_time
        self.dv = cxn.data_vault
        self.pulser = cxn.pulser
        self.grapher = cxn.grapher
        drive_freq = self.parameters.TrapFrequencies.rf_drive_frequency
        self.drive_period = 1/drive_freq
        self.time_resolution = self.pulser.get_timetag_resolution()
        self.programPulseSequence(self.record_time)

    def programPulseSequence(self, record_time):
        seq = record_timetags(TreeDict.fromdict({'RecordTimetags.record_timetags_duration': record_time}))
        seq.programSequence(self.pulser)

    def run(self, cxn, context):
        self.pulser.reset_timetags()
        self.pulser.start_single()
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        time_tags = self.pulser.get_timetags()
        self.saveData(time_tags)

    def saveData(self, time_tags):
        self.dv.cd(['','QuickMeasurements','TD-Flourescence'],True)
        name = self.dv.new('TD-Flourescence',[('time', 'ns')], [('number in bin','Arb','Arb')] )
        data = np.remainder(1e9*time_tags, self.drive_period['ns'])
        hist, bin_edges = np.histogram(data, 200)
        to_plot = np.array(np.vstack((bin_edges[1:], hist)).transpose(), dtype='float')
        self.dv.add(to_plot)
        self.grapher.plot(name, 'TD_Flourescence', False)
        print 'Saved {}'.format(name)

    def finalize(self, cxn, context):
        pass

if __name__ == '__main__':
    #normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TD_flourescence(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
