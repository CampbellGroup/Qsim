import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.deshelving_point import deshelving_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U


class deshelving_rate(QsimExperiment):
    """
    Measure population in the F7/2 state as a function of applied 760nm time. Should exhibit an
    exponential decay as population is moved from the F7/2 to the S1/2.
    """

    name = 'Deshelving Rate'

    exp_parameters = []
    exp_parameters.append(('DeshelvingRate', 'scan'))
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.remove(('VariableDeshelving', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident


    def run(self, cxn, context):
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.setup_datavault('time', 'probability')
        self.setup_grapher('Shelving')
        self.times = self.get_scan_list(self.p.DeshelvingRate.scan, 'ms')
        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break
            self.p['VariableDeshelving.duration'] = U(duration, 'ms')
            self.program_pulser(sequence)
            [doppler_counts, detection_counts] = self.run_sequence(num=2, max_runs=500)
            deshelving_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            detection_counts = np.delete(detection_counts, deshelving_errors)
            hist = self.process_data(detection_counts)
            self.plot_hist(hist, folder_name='Shelving_Histogram')
            pop = self.get_pop(detection_counts)
            self.dv.add(duration, 1 - pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = deshelving_rate(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
