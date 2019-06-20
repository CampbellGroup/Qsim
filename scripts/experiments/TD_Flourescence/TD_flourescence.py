import labrad
import numpy as np
import scipy.fftpack
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.pulse_sequences.sub_sequences.RecordTimeTags import record_timetags
from treedict import TreeDict
import time


class TD_flourescence(QsimExperiment):

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
        self.setup_datavault('bins', 'occurences')
        self.setup_grapher('TD fluorescence')
        drive_freq = self.parameters.TrapFrequencies.rf_drive_frequency
        self.drive_period = 1/drive_freq
        self.time_resolution = self.pulser.get_timetag_resolution()

    def programPulseSequence(self, record_time):
        seq = record_timetags(TreeDict.fromdict({'RecordTimetags.record_timetags_duration': record_time}))
        seq.programSequence(self.pulser)

    def run(self, cxn, context):
        self.programPulseSequence(self.record_time)
        self.pulser.reset_timetags()
        self.pulser.start_single()
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        time_tags = self.pulser.get_timetags()
        self.saveData(time_tags)

    def saveData(self, time_tags):
        data = np.remainder(time_tags, self.drive_period['ns'])
        hist, bin_edges = np.histogram(data, 200)
        #  to_plot = np.array(np.vstack((x, time_tags)).transpose(), dtype='float')
        x = range(len(bin_edges) - 1)

        for i, item in enumerate(x):
            self.dv.add([item, hist[i]])

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TD_flourescence(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
