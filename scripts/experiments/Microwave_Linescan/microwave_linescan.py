import labrad
from Qsim.scripts.pulse_sequences.microwave_point import microwave_point as sequence
from Qsim.scripts.pulse_sequences.ramsey_microwave_line_scan_point import ramsey_microwave_line_scan_point as ramsey_scan
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np
from scipy.optimize import curve_fit as fit

class MicrowaveLineScan(QsimExperiment):
    """
    Scan 12.6 GHz microwave source over the qubit transition
    """

    name = 'Microwave Line Scan'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.append(('MicrowaveLinescan', 'scan'))
    exp_parameters.append(('MicrowaveLinescan', 'linescan_type'))

    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.extend(ramsey_scan.all_required_parameters())
    exp_parameters.remove(('MicrowaveInterrogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterrogation', 'duration'))

    exp_parameters.append(('bf_fluorescence', 'crop_start_time'))
    exp_parameters.append(('bf_fluorescence', 'crop_stop_time'))

    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        data = self.setup_datavault('frequency', 'probability')  # gives the x and y names to Data Vault
        qubit = self.p.Line_Selection.qubit
        print(qubit)
        print(self.p.MicrowaveInterrogation.pulse_sequence)
        self.setup_grapher('Microwave Linescan ' + qubit)
        self.detunings = self.get_scan_list(self.p.MicrowaveLinescan.scan, 'kHz')
        mode = self.p.Modes.state_detection_mode
        self.pulser.line_trigger_state(self.p.MicrowaveInterrogation.AC_line_trigger == 'On')

        linescan_type = self.p.MicrowaveLinescan.linescan_type


        if qubit == 'qubit_0':
            center = self.p.Transitions.qubit_0
            pi_time = self.p.Pi_times.qubit_0

        elif qubit == 'qubit_plus':
            center = self.p.Transitions.qubit_plus
            pi_time = self.p.Pi_times.qubit_plus

        elif qubit == 'qubit_minus':
            center = self.p.Transitions.qubit_minus
            pi_time = self.p.Pi_times.qubit_minus

        self.p['MicrowaveInterrogation.duration'] = pi_time
        deltas, probs = [], []
        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break

            self.p['MicrowaveInterrogation.detuning'] = U(detuning, 'kHz')
            if linescan_type == 'Rabi':
                self.program_pulser(sequence)
            if linescan_type == 'Ramsey':
                self.program_pulser(ramsey_scan)

            if mode == 'Shelving':
                [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
                errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                counts = np.delete(detection_counts, errors)
            if mode == 'Standard':
                [counts] = self.run_sequence()
            if mode == 'StandardFiberEOM':
                [counts] = self.run_sequence()

            if i % self.p.StandardStateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)

            pop = self.get_pop(counts)
            self.dv.add(detuning + center['kHz'], pop)
            deltas.append(detuning + center['kHz'])
            probs.append(pop)

        if qubit != 'qubit_0':
            param_guess = [20.0, deltas[np.argmax(probs)], np.min(probs), np.max(probs) - np.min(probs)]
            popt, pcov = fit(self.sinc_fit, deltas, probs, p0=param_guess)
            self.pv.set_parameter(('Transitions', qubit, U(popt[1], 'kHz')))
            print('Updated ' + str(qubit) + ' frequency to ' + str(popt[1]) + ' kHz')


    def finalize(self, cxn, context):
        self.pulser.line_trigger_state(False)
        pass


    def sinc_fit(self, freq, omega, center, offset, scale):
        """
        This fits the sinc function created in an interleaved linescan,
        identical to the fit function in RealSimpleGrapher
        """
        return scale*(omega**2/(omega**2 + (center - freq)**2)) * np.sin(np.sqrt(omega**2 + (center - freq)**2)*np.pi/(2*omega))**2 + offset


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveLineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
