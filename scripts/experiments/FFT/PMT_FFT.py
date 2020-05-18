#!scriptscanner
import labrad
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from Qsim.scripts.pulse_sequences.sub_sequences.RecordTimeTags import record_timetags
from treedict import TreeDict
from processFFT import processFFT
from labrad.units import WithUnit as U
import numpy as np


class PMT_FFT(QsimExperiment):
    """
    Performs a fourier transform of the timetags counted by the pulser. Can be used to observe the micromotion
    of the ion since scattering rates are modulated by ion motion.
    """
    name = 'PMT_FFT'

    exp_parameters = []
    exp_parameters.append(('FFT', 'center_frequency'))
    exp_parameters.append(('FFT', 'average'))
    exp_parameters.append(('FFT', 'frequency_offset'))
    exp_parameters.append(('FFT', 'frequency_span'))
    exp_parameters.append(('FFT', 'record_time'))
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.pmt = cxn.normalpmtflow
        self.pulser = cxn.pulser
        self.init_mode = self.pmt.getcurrentmode()
        self.init_freq = self.pulser.frequency('369DP')
        self.pmt.set_mode('Normal')
        self.processor = processFFT()

    def programPulseSequence(self, record_time):
        seq = record_timetags(TreeDict.fromdict({'RecordTimetags.record_timetags_duration': record_time}))
        seq.programSequence(self.pulser)

    def run(self, cxn, context):

        self.set_scannable_parameters()
        self.pulser.frequency('369DP', self.freq)
        self.programPulseSequence(self.record_time)
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
            new_pwr =  self.processor.getPowerSpectrum(self.freqs, timetags, self.record_time, U(10.0, 'ns'))
            np.add(pwr, new_pwr, out=pwr, casting="unsafe")
            #pwr += self.processor.getPowerSpectrum(self.freqs, timetags, self.record_time, U(10.0, 'ns'))
        pwr = pwr / float(self.average)
        data = np.array(np.vstack((self.freqs, pwr)).transpose(), dtype='float')
        self.dv.add(data)

    def set_scannable_parameters(self):
        detuning = self.p.DopplerCooling.detuning
        self.freq = detuning / 2.0 + self.p.Transitions.main_cooling_369/2.0 + U(200.0, 'MHz')  # divide by 2 for the double pass
        self.record_time = self.p.FFT.record_time
        self.average = int(self.p.FFT.average)
        self.center_freq = self.p.FFT.center_frequency
        self.freq_span = self.p.FFT.frequency_span
        self.freq_offset = self.p.FFT.frequency_offset
        self.freqs = self.processor.computeFreqDomain(self.record_time['s'], self.freq_span['Hz'],
                                                      self.freq_offset['Hz'], self.center_freq['Hz'])
    def finalize(self, cxn, context):

        self.pulser.frequency('369DP', self.init_freq)
        self.pmt.set_mode(self.init_mode)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = PMT_FFT(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
