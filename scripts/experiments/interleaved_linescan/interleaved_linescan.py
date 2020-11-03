import labrad
from Qsim.scripts.pulse_sequences.interleaved_point import interleaved_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit
import numpy as np


class InterleavedLinescan(QsimExperiment):
    """
    Scan the 369 laser with the AOM double pass interleaved
    with doppler cooling to reveal the lineshape. This experiment helps
    to diagnose problems with micromotion compensation and cooling laser
    intensity
    """

    name = 'Interleaved Line Scan'

    exp_parameters = []
    exp_parameters.append(('InterleavedLinescan', 'repititions'))
    exp_parameters.append(('InterleavedLinescan', 'line_scan'))

    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('DipoleInterogation', 'frequency'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.reg = cxn.registry
        self.pulser = cxn.pulser
        self.reg.cd(['', 'settings'])

    def run(self, cxn, context):

        self.pulser.line_trigger_state(False)
        self.setup_datavault('frequency', 'photons')  # gives the x and y names to Data Vault
        self.setup_grapher('Interleaved Linescan')
        self.detunings = self.get_scan_list(self.p.InterleavedLinescan.line_scan, 'MHz')
        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                return should_break
            # self.p.Transitions.main_cooling_369 divide by 2 for the double pass
            freq = WithUnit(detuning, 'MHz')/2.0 + self.p.ddsDefaults.DP369_freq
            self.program_pulser(freq, detuning)

    def program_pulser(self, freq, detuning):
        self.p['DipoleInterogation.frequency'] = freq
        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(int(self.p.InterleavedLinescan.repititions))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        time_tags = self.pulser.get_timetags()
        counts = len(time_tags)
        self.pulser.reset_timetags()
        self.dv.add(detuning, counts)

#    def map_power(self, power, freq):
#        low = 0.0
#        coeff = list(self.reg.get('AOM_calibration'))
#        low = np.polyval(coeff, freq['MHz'] - 192.0)
#        dB_increase = WithUnit(np.log10(1/low), 'dBm')
#        adj_power = power + 15.0*abs(dB_increase)
#        if adj_power > WithUnit(-5.0, 'dBm'):
#            adj_power = WithUnit(-5.0, 'dBm')

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = InterleavedLinescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
