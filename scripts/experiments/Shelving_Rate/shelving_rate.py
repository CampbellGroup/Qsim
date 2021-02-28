import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.shelving_point import shelving_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U


class shelving_rate(QsimExperiment):
    """
    Measure 411nm shelving rate to the F7/2
    """

    name = 'Shelving Rate'

    exp_parameters = []
    exp_parameters.append(('ShelvingRate', 'scan'))
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('Shelving', 'duration'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.remove(('MicrowaveInterrogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterrogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.setup_datavault('time', 'probability')
        self.setup_grapher('Shelving')
        self.p['MicrowaveInterrogation.duration'] = self.p.Pi_times.qubit_0
        self.p['MicrowaveInterrogation.detuning'] = U(0.0, 'kHz')
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.times = self.get_scan_list(self.p.ShelvingRate.scan, 'ms')
        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break
            self.p['Shelving.duration'] = U(duration, 'ms')
            self.program_pulser(sequence)
            [doppler_counts, detection_counts] = self.run_sequence(num=2, max_runs=500)
            deshelving_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            detection_counts = np.delete(detection_counts, deshelving_errors)
            hist = self.process_data(detection_counts)
            self.plot_hist(hist, folder_name='Shelving_Histogram')
            pop = self.get_pop(detection_counts)
            self.dv.add(duration, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = shelving_rate(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
