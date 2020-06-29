import labrad
import numpy as np
from Qsim.scripts.pulse_sequences.optical_pumping_point import optical_pumping_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U


class quadrupole_optical_pumping_linescan(QsimExperiment):


    name = 'QuadrupoleOpticalPumpingLinescan'

    exp_parameters = []

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('OpticalPumping', 'duration'))
    exp_parameters.remove(('OpticalPumping', 'quadrupole_op_detuning'))
    exp_parameters.append(('OpticalPumping', 'quadrupole_op_duration'))
    exp_parameters.append(('QuadrupoleOpticalPumpingLinescan', 'scan'))
    exp_parameters.append(('OpticalPumping', 'method'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('Modes', 'state_detection_mode'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):
        self.setup_datavault('frequency', 'probability')
        self.setup_grapher('QuadrupoleOpticalPumpingLinescan')
        self.frequencies = self.get_scan_list(self.p.QuadrupoleOpticalPumpingLinescan.scan, 'MHz')
        for i, freq in enumerate(self.frequencies):
            should_break = self.update_progress(i/float(len(self.frequencies)))
            if should_break:
                break
            self.p['OpticalPumping.method'] = 'QuadrupoleOnly'
            if self.p.Modes.state_detection_mode == 'Shelving':
                self.p['OpticalPumping.duration'] = U(0.0, 'us')
                self.p['OpticalPumping.quadrupole_op_duration'] = self.p.OpticalPumping.quadrupole_op_duration
                self.p['OpticalPumping.quadrupole_op_detuning'] = U(freq, 'MHz')
                self.p['Modes.state_detection_mode'] = 'Shelving'
                self.program_pulser(sequence)
                [doppler_counts, detection_counts] = self.run_sequence(num=2, max_runs=500)
                deshelving_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                detection_counts = np.delete(detection_counts, deshelving_errors)
            elif self.p.Modes.state_detection_mode == 'Standard':
                self.p['OpticalPumping.duration'] = U(0.0, 'us')
                self.p['OpticalPumping.quadrupole_op_duration'] = self.p.OpticalPumping.quadrupole_op_duration
                self.p['OpticalPumping.quadrupole_op_detuning'] = U(freq, 'MHz')
                self.p['Modes.state_detection_mode'] = 'Standard'
                self.program_pulser(sequence)
                [detection_counts] = self.run_sequence(num=1, max_runs=1000)

            hist = self.process_data(detection_counts)
            self.plot_hist(hist)
            pop = self.get_pop(detection_counts)
            self.dv.add(freq, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = quadrupole_optical_pumping_linescan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
