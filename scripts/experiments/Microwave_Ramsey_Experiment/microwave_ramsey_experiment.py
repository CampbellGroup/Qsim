import labrad
from Qsim.scripts.pulse_sequences.microwave_ramsey_point import microwave_ramsey_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MicrowaveRamseyExperiment(QsimExperiment):
    """
    Scan delay time between microwave pulses with variable pulse area
    """

    name = 'Microwave Ramsey Experiment'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('Transitions', 'qubit_0'))
    exp_parameters.append(('Transitions', 'rabi_freq_qubit_0')) #paramter currently unused --> need rabi freq.
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.append(('MicrowaveInterogation', 'duration'))
    exp_parameters.append(('MicrowaveInterogation', 'detuning'))
    exp_parameters.append(('MicrowaveDelay', 'delay_time'))
    exp_parameters.append(('EmptySequence', 'duration'))

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

        self.setup_datavault('time', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Microwave Ramsey Experiment')
        self.dark_time = self.get_scan_list(self.p.MicrowaveDelay.delay_time, 'us')
        for i, dark_time in enumerate(self.dark_time):
            should_break = self.update_progress(i/float(len(self.dark_time)))
            if should_break:
                break
            delay = U(dark_time, 'us')
            counts = self.program_pulser(delay)
            hist = self.process_data(counts)
            pop = self.get_pop(counts)
            self.dv.add(dark_time, pop)

    def program_pulser(self, delay):
        self.p['EmptySequence.duration'] = delay
        pulse_sequence = sequence(self.p)
        pulse_sequence.programSequence(self.pulser)
        self.pulser.start_number(int(self.p.StateDetection.repititions))
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        counts = self.pulser.get_readout_counts()
        self.pulser.reset_readout_counts()
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
    exprt = MicrowaveRamseyExperiment(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
