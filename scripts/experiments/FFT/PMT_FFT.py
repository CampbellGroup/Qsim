#!scriptscanner
import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.pulse_sequences.sub_sequences.RecordTimeTags import record_timetags
from treedict import TreeDict
from processFFT import processFFT
from labrad.units import WithUnit as U
import numpy as np


class PMT_FFT(QsimExperiment):

    name = 'PMT_FFT'

    '''
    Takes FFT of incoming PMT Counts

    '''

    exp_parameters = []
    exp_parameters.append(('FFT', 'center_frequency'))
    exp_parameters.append(('FFT', 'average'))
    exp_parameters.append(('FFT', 'frequency_offset'))
    exp_parameters.append(('FFT', 'frequency_span'))
    exp_parameters.append(('FFT', 'record_time'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.pulser = cxn.pulser
        self.processor = processFFT()
        self.record_time = self.p.FFT.record_time
        self.average = int(self.p.FFT.average)
        self.center_freq = self.p.FFT.center_frequency
        self.freq_span = self.p.FFT.frequency_span
        self.freq_offset = self.p.FFT.frequency_offset
        self.freqs = self.processor.computeFreqDomain(self.record_time['s'], self.freq_span['Hz'],
                                                      self.freq_offset['Hz'], self.center_freq['Hz'])
        self.programPulseSequence(self.record_time)

    def programPulseSequence(self, record_time):
        seq = record_timetags(TreeDict.fromdict({'RecordTimetags.record_timetags_duration': record_time}))
        seq.programSequence(self.pulser)

    def run(self, cxn, context):

        self.setup_datavault('Frequencies', 'Amplitude')
        self.setup_grapher('PMT FFT')

        pwr = np.zeros_like(self.freqs)
        for i in range(self.average):
            seq = record_timetags(TreeDict.fromdict({'RecordTimetags.record_timetags_duration': self.record_time}))
            seq.programSequence(self.pulser)
            self.pulser.reset_timetags()
            self.pulser.start_single()
            self.pulser.wait_sequence_done()
            self.pulser.stop_sequence()
            timetags = self.pulser.get_timetags()
            should_break = self.update_progress(i/float(self.average))
            if should_break:
                break
            pwr += self.processor.getPowerSpectrum(self.freqs, timetags, self.record_time, U(10.0, 'ns'))
        pwr = pwr / float(self.average)
        data = np.array(np.vstack((self.freqs, pwr)).transpose(), dtype='float')
        self.dv.add(data)


    def finalize(self, cxn, context):
        '''
        In the finalize function we can close any connections or stop any
        processes that are no longer necessary.
        '''
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = PMT_FFT(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)