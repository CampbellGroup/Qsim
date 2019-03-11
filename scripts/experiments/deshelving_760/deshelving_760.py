import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.deshelving_point import deshelving_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U

class DeshelvingRate(QsimExperiment):
    """
    Measure 760nm deshelving rate to the F7/2
    """

    name = 'DeshelvingRate'

    exp_parameters = []
    exp_parameters.append(('DeshelvingRate', 'scan'))
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.append(('StateDetection', 'repititions'))
    exp_parameters.append(('StateDetection', 'state_readout_threshold'))
    exp_parameters.append(('StateDetection', 'points_per_histogram'))
    exp_parameters.append(('StateDetection', 'doppler_counts_threshold'))
    exp_parameters.remove(('VariableDeshelving', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.setup_datavault('time', 'probability')
        self.setup_grapher('DeshelvingRate')
        self.times = self.get_scan_list(self.p.DeshelvingRate.scan, 'ms')
        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break
            self.p['VariableDeshelving.duration'] = U(duration, 'ms')
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
            self.dv.add(duration, 1 - pop)

    def finalize(self, cxn, context):
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DeshelvingRate(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
