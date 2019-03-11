import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.shelving_point import shelving_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U

class ShelvingRate(QsimExperiment):
    """
    Measure 411nm shelving rate to the F7/2
    """

    name = 'ShelvingRate'

    exp_parameters = []
    exp_parameters.append(('ShelvingRate', 'scan'))
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('Shelving', 'duration'))
    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.append(('StateDetection', 'points_per_histogram'))
    exp_parameters.append(('StateDetection', 'doppler_counts_threshold'))


    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.setup_datavault('time', 'probability')
        self.setup_grapher('ShelvingRate')
        self.times = self.get_scan_list(self.p.ShelvingRate.scan, 'ms')
        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break
            self.p['Shelving.duration'] = U(duration, 'ms')
            self.program_pulser(sequence)
            counts = self.run_sequence()
            doppler_counts = counts[0::2]
            deshelving_errors = np.where(doppler_counts <= self.p.StateDetection.doppler_counts_threshold)
            print deshelving_errors
            detection_counts = np.delete(counts[1::2], deshelving_errors)
            if i % self.p.StateDetection.points_per_histogram == 0:
                hist = self.process_data(detection_counts)
                self.plot_hist(hist)
            pop = self.get_pop(detection_counts)
            self.dv.add(duration, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = ShelvingRate(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
