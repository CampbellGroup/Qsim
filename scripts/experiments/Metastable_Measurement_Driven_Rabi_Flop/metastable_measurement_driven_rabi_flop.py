import labrad
from Qsim.scripts.pulse_sequences.metastable_measurement_driven_rabi_point import metastable_measurement_driven_rabi_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np


class metastable_measurement_driven_rabi_flop(QsimExperiment):

    name = 'Metastable Measurement Driven Rabi Flop'

    exp_parameters = []
    exp_parameters.append(('MetastableMeasurementDrivenGate', 'scan'))
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('time', 'probability')
        self.setup_grapher('MeasurementDrivenRabiFlop')
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.num_pulses = self.get_scan_list(self.p.MetastableMeasurementDrivenGate.scan, '')
        for i, pulse_num in enumerate(self.num_pulses):

            should_break = self.update_progress(i / float(len(self.num_pulses)))
            if should_break:
                break

            self.p['MetastableMeasurementDrivenGate.current_pulse_index'] = pulse_num
            self.program_pulser(sequence)
            [doppler_counts, herald_counts, failed_gate_counts, detection_counts] = self.run_sequence(max_runs=250, num=4)

            # work up the results to return a success and failure rate
            doppler_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
            failed_heralding = np.where(herald_counts >= self.p.ShelvingStateDetection.state_readout_threshold)
            failed_gate = np.where(failed_gate_counts >= self.p.ShelvingStateDetection.state_readout_threshold)
            all_errors = np.unique(np.concatenate((failed_heralding[0], doppler_errors[0], failed_gate[0])))

            # get rid of failed doppler counts, failed heralding, and failed gate experiments
            detection_fixed = np.delete(detection_counts, all_errors)

            uW_time = pulse_num * self.p.Pi_times.metastable_qubit / self.p.MetastableMeasurementDrivenGate.total_num_sub_pulses
            prob = len(np.where(detection_fixed >= self.p.ShelvingStateDetection.state_readout_threshold)[0])/float(len(detection_fixed))
            self.dv.add(uW_time['us'], prob) #, float(len(detection_fixed)))
            print('Number of experiments = ' + str(len(detection_fixed)))
            print('Microwave interrogation time = ' + str(uW_time) + ', probability = ' + str(prob))


    def finalize(self, cxn, context):
        pass

    #def setup_datavault_rabi(self, x_axis, y_axis):
    #    self.counts_context = self.dv.context()
    #    self.dv.cd(['', self.name], True, context=self.counts_context)
    #    self.dataset = self.dv.new(self.name, [(x_axis, 'us')],
    #                               [(y_axis, 'probability', 'num'), (y_axis, 'number_experiments', 'num')],
    #                               context=self.counts_context)
    #    for parameter in self.p:
    #        self.dv.add_parameter(parameter, self.p[parameter], context=self.counts_context)


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = metastable_measurement_driven_rabi_flop(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)