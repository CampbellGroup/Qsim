import labrad
from Qsim.scripts.pulse_sequences.sub_sequences.DipoleInterogation import dipole_interogation as sequence
from Qsim.scripts.pulse_sequences.sub_sequences.DopplerCooling import doppler_cooling
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment


class InterleavedLinescan(QsimExperiment):
    """
    Scan the 369 laser with the AOM double pass interleaved
    with doppler cooling.
    """

    name = 'Interleaved Line Scan'

    exp_parameters = []
    exp_parameters.append(('InterleavedLinescan', 'doppler_cooling_time'))
    exp_parameters.append(('InterleavedLinescan', 'interogation_repititions'))
    exp_parameters.append(('InterleavedLinescan', 'line_scan'))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('DipoleInterogation', 'interogation_frequency'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = self.cxn.pulser
        self.dds_channel = '369'

    def run(self, cxn, context):

        self.frequencies = self.get_scan_list(self.p.InterleavedLinescan.line_scan, 'MHz')
        power = self.p.DipoleInterogation.interogation_power
        for freq in self.frequencies:
            self.program_pulser(freq)

    def program_pulser(self, freq):
        self.pulser.reset_readout_counts()
        self.p['DipoleInterogation.interogation_frequency'] = freq
        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_single()
        self.pulser.wait_sequence_done()
        readout = self.pulser.get_readout_counts
        print readout

    def finalize(self, cxn, context):
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = InterleavedLinescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
