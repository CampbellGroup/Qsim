import labrad
from Qsim.scripts.pulse_sequences.microwave_point import microwave_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MicrowaveLineScan(QsimExperiment):
    """
    Scan 12.6 GHz microwave source over the qubit transition
    """

    name = 'Microwave Line Scan'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('Transitions', 'qubit_0'))
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.append(('MicrowaveLinescan', 'scan'))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('MicrowaveInterogation','detuning'))


    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.reg = cxn.registry
        self.reg.cd(['','settings'])
        self.pmt = self.cxn.normalpmtflow
        self.init_mode = self.pmt.getcurrentmode()
        self.pmt.set_mode('Normal')
        self.pulser = self.cxn.pulser

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Microwave Linescan')
        self.detunings = self.get_scan_list(self.p.MicrowaveLinescan.scan, 'kHz')
        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break
            freq = U(detuning, 'kHz')
            counts = self.program_pulser(freq)
            hist = self.process_data(counts)
            pop = self.get_pop(counts)
            self.dv.add(detuning, pop)

    def program_pulser(self, detuning):
        self.p['MicrowaveInterogation.detuning'] = detuning
        reps_completed = 0
        counts = np.array([])
        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        while int(reps_completed) < self.p.StateDetection.repititions:
            if self.p.StateDetection.repititions - reps_completed >= 1000:
                self.pulser.start_number(1000)
                reps_completed += 1000
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()
                temp_counts = self.pulser.get_readout_counts()
                self.pulser.reset_readout_counts()
                counts = np.concatenate((counts, temp_counts))
            elif self.p.StateDetection.repititions - reps_completed  < 1000:
                self.pulser.start_number(int(self.p.StateDetection.repititions - reps_completed))
                self.pulser.wait_sequence_done()
                self.pulser.stop_sequence()
                temp_counts = self.pulser.get_readout_counts()
                self.pulser.reset_readout_counts()
                reps_completed += int(self.p.StateDetection.repititions)
                counts = np.concatenate((counts, temp_counts))
        return counts

    def process_data(self, counts):
        data = np.column_stack((np.arange(self.p.StateDetection.repititions), counts))
        y = np.histogram(data[:, 1], int(np.max([data[:, 1].max() - data[:, 1].min(), 1])))
        counts = y[0]
        bins = y[1][:-1]
        if bins[0] < 0:
            bins = bins + .5
        hist = np.column_stack((bins, counts))
        return hist


    def get_pop(self, counts):
        self.thresholdVal = self.p.StateDetection.state_readout_threshold
        prob = len(np.where(counts > self.thresholdVal)[0])/float(len(counts))
        return prob


    def finalize(self, cxn, context):
        self.pmt.set_mode(self.init_mode)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveLineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
