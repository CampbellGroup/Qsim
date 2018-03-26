import labrad
from Qsim.scripts.pulse_sequences.microwave_ramsey_point import microwave_ramsey_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U


class MicrowaveRamseyExperiment(QsimExperiment):
    """
    Scan delay time between microwave pulses with variable pulse area
    """

    name = 'Microwave Ramsey Experiment'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('Transitions', 'qubit_0'))
    exp_parameters.append(('Transitions', 'rabi_freq_qubit_0'))
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.append(('MicrowaveInterogation', 'duration'))
    exp_parameters.append(('MicrowaveInterogation', 'detuning'))
    exp_parameters.append(('MicrowaveDelay', 'delay_time'))
    exp_parameters.append(('StateDetection', 'points_per_histogram'))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('EmptySequence', 'duration'))
    exp_parameters.remove(('MicrowaveInterogation', 'detuning'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('time', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Microwave Ramsey Experiment')
        self.dark_time = self.get_scan_list(self.p.MicrowaveDelay.delay_time, 'us')
        for i, dark_time in enumerate(self.dark_time):
            should_break = self.update_progress(i/float(len(self.dark_time)))
            if should_break:
                break
            self.p['EmptySequence.duration'] = U(dark_time, 'us')
            self.program_pulser(sequence)
            counts = self.run_sequence()
            if i % self.p.StateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)
            pop = self.get_pop(counts)
            self.dv.add(dark_time, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveRamseyExperiment(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
