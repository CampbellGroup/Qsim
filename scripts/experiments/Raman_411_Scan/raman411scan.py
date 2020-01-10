import labrad
from Qsim.scripts.pulse_sequences.raman_411_point import raman_411_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U


class Raman411LineScan(QsimExperiment):

    name = 'Raman 411 Scan'

    exp_parameters = []
    exp_parameters.append(('Raman411Linescan', 'scan'))
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('Raman411Interogation', 'detuning2'))
    exp_parameters.remove(('Line_Selection', 'qubit'))

    exp_parameters.append(('StandardStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'probability')
        self.setup_grapher('Raman_411_Linescan')
        self.detunings = self.get_scan_list(self.p.Raman411Linescan.scan, 'kHz')

        for i, detuning in enumerate(self.detunings):

            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break

            self.p['Modes.state_detection_mode'] = 'Standard'
            self.p['Raman411Interogation.detuning2'] = U(detuning, 'kHz')
            self.p['Line_Selection.qubit'] = 'qubit_plus'
            pi_time = self.p.Pi_times.qubit_plus
            self.p['MicrowaveInterogation.duration'] = pi_time
            self.program_pulser(sequence)
            [counts] = self.run_sequence()

            hist = self.process_data(counts)
            self.plot_hist(hist)
            pop = self.get_pop(counts)
            self.dv.add(detuning, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = Raman411LineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
