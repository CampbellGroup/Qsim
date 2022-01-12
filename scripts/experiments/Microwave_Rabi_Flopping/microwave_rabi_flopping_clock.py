import labrad
from Qsim.scripts.pulse_sequences.microwave_point_clock import microwave_point_clock as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np
from scipy.optimize import curve_fit as fit


class MicrowaveRabiFloppingClock(QsimExperiment):
    """
    repeatedly prepare the |0> state, interrogate with resonant microwaves for
    a variable time t and measure the population in the bright state
    """

    name = 'Microwave Rabi Flopping Clock'

    exp_parameters = []
    exp_parameters.append(('RabiFlopping', 'scan'))
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('MicrowaveInterrogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser

    def run(self, cxn, context):

        self.set_default_parameters()
        self.setup_datavault('time', 'probability')
        self.setup_grapher('Rabi Flopping qubit_0')

        self.times = np.arange(0.1, 6.1 * self.pi_time, 3.2)
        probs, times = [], []
        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                self.pulser.line_trigger_state(False)
                break
            self.p['MicrowaveInterrogation.duration'] = U(duration, 'us')
            self.program_pulser(sequence)
            [counts] = self.run_sequence()


            if i % self.p.StandardStateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)

            pop = self.get_pop(counts)
            self.dv.add(duration, pop)
            probs.append(pop)
            times.append(duration)

        popt, pcov = fit(self.rabi, times, probs, p0=[1.0, self.pi_time, 0.0, 0.0],
                         bounds=(0.0, [1.0, 200.0, 3.14, 1.0]))
        self.pv.set_parameter(('Pi_times', 'qubit_0', U(popt[1], 'us')))
        print('Updated qubit_0 pi_time to ' + str(popt[1])[:8] + ' microseconds')

        return popt[1]

    def set_default_parameters(self):
        self.p['OpticalPumping.method'] = 'Standard'
        self.p['StandardStateDetection.repetitions'] = 400.0
        self.p['Line_Selection.qubit'] = 'qubit_0'
        self.pi_time = self.pv.get_parameter('Pi_times', 'qubit_0')['us']

    def rabi(self, t, A, pi_time, phase, offset):
        return A * np.sin(np.pi * t /(2.0 * pi_time) + phase)**2 + offset

    def finalize(self, cxn, context):
        pass

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveRabiFloppingClock(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
