import labrad
from Qsim.scripts.pulse_sequences.interleaved_point import interleaved_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit
import numpy as np


class InterleavedLinescan(QsimExperiment):
    """
    Scan the 369 laser with the AOM double pass interleaved
    with doppler cooling.
    """

    name = 'Interleaved Line Scan'

    exp_parameters = []
    exp_parameters.append(('InterleavedLinescan', 'interogation_repititions'))
    exp_parameters.append(('InterleavedLinescan', 'line_scan'))
    exp_parameters.append(('InterleavedLinescan', 'line_center'))
    exp_parameters.append(('InterleavedLinescan', 'use_calibration'))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('DipoleInterogation', 'interogation_frequency'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pmt = self.cxn.normalpmtflow
        self.init_mode = self.pmt.getcurrentmode()
        self.pmt.set_mode('Normal')
        self.pulser = self.cxn.pulser
        self.dds_channel = '369'
        self.init_power = self.p.DipoleInterogation.interogation_power

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'photons')  # gives the x and y names to Data Vault
        self.setup_grapher('Interleaved Linescan')
        self.frequencies = self.get_scan_list(self.p.InterleavedLinescan.line_scan, 'MHz')
        for i, freq in enumerate(self.frequencies):
            should_break = self.update_progress(i/float(len(self.frequencies)))
            if should_break:
                break
            freq = WithUnit(freq, 'MHz')
            self.program_pulser(freq)

    def program_pulser(self, freq):
        self.p['DipoleInterogation.interogation_frequency'] = freq
        if self.p.InterleavedLinescan.use_calibration:
            cal_power = self.map_power(self.init_power, freq)
            self.p['DipoleInterogation.interogation_power'] = cal_power
        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(int(self.p.InterleavedLinescan.interogation_repititions['s']))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        time_tags = self.pulser.get_timetags()
        counts = len(time_tags)
        relative_freq = (freq - self.p.InterleavedLinescan.line_center)*2
        self.pulser.reset_timetags()
        self.dv.add(relative_freq['MHz'], counts)

    def map_power(self, power, freq):
        coeff = [ -6.24008797e-33,  1.19968556e-30,  1.60281888e-28,  -4.39832776e-26, -8.51414472e-25,   6.57202702e-22,
                  -1.22211445e-20,  -5.25158507e-18, 2.01151126e-16,   2.44693693e-14,  -1.25696347e-12,  -6.71593941e-11,
                  4.16006414e-09,   1.02344346e-07,  -7.46435947e-06,  -7.14960823e-05, 6.57396410e-03,   7.43451182e-03,
                  -2.48652156e+00,   1.40807172e+01, 3.17203009e+03]
        coeff.reverse()
        int_increase = 0
        for i, c in enumerate(coeff):
            int_increase += c*(freq['MHz'] - 191.5)**i
        gain_fit = -0.003475*freq['MHz']**2 + 1.3978*freq['MHz'] - 126.69
        dB_increase = WithUnit(10*np.log10(3192.09/int_increase),'dBm')
        dB_increase = WithUnit(10*np.log10(11.877/gain_fit),'dBm')
        adj_power = power + dB_increase
        if adj_power > WithUnit(-8.0, 'dBm'):
            adj_power = WithUnit(-8.0, 'dBm')
        return adj_power


    def finalize(self, cxn, context):
        self.pmt.set_mode(self.init_mode)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = InterleavedLinescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
