import labrad
from Qsim.scripts.pulse_sequences.metastable_measurement_driven_gate import metastable_measurement_driven_gate as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MetastableMeasurementDrivenGate(QsimExperiment):

    name = 'Metastable Measurement Driven Gate'

    exp_parameters = []
    exp_parameters.extend(sequence.all_required_parameters())


    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('number', 'probability')  
        self.setup_grapher('Metastable Measurement Driven Gate')

        self.p['Modes.state_detection_mode'] = 'Shelving'

        self.pulse_num = self.get_scan_list(self.p.MetastableMeasurementDrivenGate.scan, 'num')
        for i, duration in enumerate(self.pulse_num):

            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break
            
            self.program_pulser(heralded_sequence)
            [doppler_counts, herald_counts, detection_counts] = self.run_sequence(max_runs=333, num=3)
            
            failed_heralding = np.where(herald_counts >= self.p.ShelvingStateDetection.state_readout_threshold)
            doppler_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            
            all_errors = np.unique(np.concatenate((failed_heralding[0], doppler_errors[0])))
            counts = np.delete(detection_counts, all_errors)

            hist = self.process_data(counts)
            self.plot_hist(hist)
            pop = self.get_pop(counts)
            self.dv.add(duration, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MetastableMicrowaveRabiFlopping(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
