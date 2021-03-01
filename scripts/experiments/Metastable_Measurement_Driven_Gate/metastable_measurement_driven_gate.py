import labrad
from Qsim.scripts.pulse_sequences.metastable_measurement_driven_gate import metastable_measurement_driven_gate as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np


class metastable_measurement_driven_gate(QsimExperiment):

    name = 'Metastable Measurement Driven Gate'

    exp_parameters = []
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault_counts('number', 'counts')

        self.p['Modes.state_detection_mode'] = 'Shelving'

        self.program_pulser(sequence)
        [doppler_counts, herald_counts, failed_gate_counts, detection_counts] = self.run_sequence(max_runs=250, num=4)

        num = np.ones(len(doppler_counts))*self.p.MetastableMeasurementDrivenGate.total_num_sub_pulses
        self.dv.add(np.column_stack((num, doppler_counts, herald_counts, failed_gate_counts, detection_counts)), context=self.counts_context)

        # work up the results to return a success and failure rate
        doppler_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
        failed_heralding = np.where(herald_counts >= self.p.ShelvingStateDetection.state_readout_threshold)

        all_errors = np.unique(np.concatenate((failed_heralding[0], doppler_errors[0])))

        failed_gate_fixed = np.delete(failed_gate_counts, all_errors)
        detection_fixed = np.delete(detection_counts, all_errors)

        total_num_experiments = float(len(failed_gate_fixed))

        failed_gate = np.where(failed_gate_fixed >= self.p.ShelvingStateDetection.state_readout_threshold)
        detection_fixed = np.delete(detection_fixed, failed_gate)
        success_gate = np.where(detection_fixed >= self.p.ShelvingStateDetection.state_readout_threshold)

        print('Total number of heralded experiments = ' + str(total_num_experiments))
        print('Gate success rate = ' + str(len(success_gate[0])/total_num_experiments))
        print('Gate failure rate = ' + str(len(failed_gate[0])/total_num_experiments))

    def finalize(self, cxn, context):
        pass

    def setup_datavault_counts(self, x_axis, y_axis):
        self.counts_context = self.dv.context()
        self.dv.cd(['', self.name], True, context=self.counts_context)
        self.dataset = self.dv.new(self.name, [(x_axis, 'num')],
                                   [(y_axis, 'Doppler_Counts', 'num'), (y_axis, 'Herald_Counts', 'num'),
                                   (y_axis, 'Shelving_Counts', 'num'), (y_axis, 'Metastable_Counts', 'num')],
                                   context=self.counts_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter], context=self.counts_context)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = metastable_measurement_driven_gate(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
