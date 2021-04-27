import labrad
from Qsim.scripts.pulse_sequences.microwave_point_minus import microwave_point_minus as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np
from scipy.optimize import curve_fit as fit

class MicrowaveLineScanMinus(QsimExperiment):


    name = 'Microwave Line Scan Minus'

    exp_parameters = []
    exp_parameters.append(('MicrowaveLinescan', 'scan'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.remove(('MicrowaveInterrogation', 'detuning'))
    exp_parameters.remove(('MicrowaveInterrogation', 'duration'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Microwave Linescan qubit_minus')
        self.detunings = self.get_scan_list(self.p.MicrowaveLinescan.scan, 'kHz')

        self.set_default_parameters()

        deltas, probs = [], []
        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break

            self.p['MicrowaveInterrogation.detuning'] = U(detuning, 'kHz')
            self.program_pulser(sequence)

            [counts] = self.run_sequence()

            if i % self.p.StandardStateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)

            pop = self.get_pop(counts)
            self.dv.add(detuning + self.p.Transitions.qubit_minus['kHz'], pop)
            deltas.append(detuning + self.p.Transitions.qubit_minus['kHz'])
            probs.append(pop)

        param_guess = [20.0, deltas[np.argmax(probs)], np.min(probs), np.max(probs) - np.min(probs)]
        popt, pcov = fit(self.sinc_fit, deltas, probs, p0=param_guess)
        self.pv.set_parameter(('Transitions', 'qubit_minus', U(popt[1], 'kHz')))
        print('Updated qubit_minus frequency to ' + str(popt[1]) + ' kHz')

        return should_break


    def set_default_parameters(self):
        self.p['MicrowaveInterrogation.duration'] = self.p.Pi_times.qubit_minus
        self.p['OpticalPumping.method'] = 'Standard'

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
    exprt = MicrowaveLineScanMinus(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
