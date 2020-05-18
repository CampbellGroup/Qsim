import labrad
from Qsim.scripts.pulse_sequences.microwave_point import microwave_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MicrowaveLineScan(QsimExperiment):
    """
    Scan 12.6 GHz microwave source over the qubit transition
    """

    name = 'Microwave Line Scan'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.append(('MicrowaveLinescan', 'scan'))

    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('MicrowaveInterogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterogation', 'duration'))

    exp_parameters.append(('bf_fluorescence', 'crop_start_time'))
    exp_parameters.append(('bf_fluorescence', 'crop_stop_time'))

    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        init_microwave_pulse_sequence = self.p.MicrowaveInterogation.pulse_sequence
        init_optical_pumping_method = self.p.OpticalPumping.method

        #self.p['MicrowaveInterogation.pulse_sequence'] = 'standard'
        self.p['OpticalPumping.method'] = 'Standard'

        data = self.setup_datavault('frequency', 'probability')  # gives the x and y names to Data Vault
        qubit = self.p.Line_Selection.qubit
        self.setup_grapher('Microwave Linescan ' + qubit)
        self.detunings = self.get_scan_list(self.p.MicrowaveLinescan.scan, 'kHz')
        mode = self.p.Modes.state_detection_mode
        if qubit == 'qubit_0':
            center = self.p.Transitions.qubit_0
            pi_time = self.p.Pi_times.qubit_0

        elif qubit == 'qubit_plus':
            center = self.p.Transitions.qubit_plus
            pi_time = self.p.Pi_times.qubit_plus

        elif qubit == 'qubit_minus':
            center = self.p.Transitions.qubit_minus
            pi_time = self.p.Pi_times.qubit_minus

        self.p['MicrowaveInterogation.duration'] = pi_time

        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break
            self.p['MicrowaveInterogation.detuning'] = U(detuning, 'kHz')
            self.program_pulser(sequence)
            if mode == 'Shelving':
                [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
                errors = np.where(doppler_counts <= self.p.ShelvingDopplerCooling.doppler_counts_threshold)
                counts = np.delete(detection_counts, errors)
            if mode == 'Standard':
                [counts] = self.run_sequence()

            if i % self.p.StandardStateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)
            pop = self.get_pop(counts)

            self.dv.add(detuning + center['kHz'], pop)

        self.p['MicrowaveInterogation.pulse_sequence'] = init_microwave_pulse_sequence
        self.p['OpticalPumping.method'] = init_optical_pumping_method

        return should_break

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveLineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
