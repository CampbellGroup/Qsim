import labrad
from Qsim.scripts.pulse_sequences.microwave_point import microwave_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np
import time


class RabiPointTracker(QsimExperiment):
    """
    Scan the 369 laser with the AOM double pass interleaved
    with doppler cooling.
    """

    name = 'Rabi Point Tracker'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'repititions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('MicrowaveInterogation', 'AC_line_trigger'))
    exp_parameters.append(('RabiPointTracker', 'number_pi_times'))
    exp_parameters.append(('RabiPointTracker', 'shelving_fidelity_drift_tracking'))
    exp_parameters.append(('RabiPointTracker', 'pi_time_feedback'))
    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('MicrowaveInterogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context

    def run(self, cxn, context):
        """
        We are going to repeat the same rabi point over and over indefinitely and
        plot the probability of being in the up state as a function of real lab time,
        which will be kept track of using the native 'time' function in python
        """
        qubit = self.p.Line_Selection.qubit
        mode = self.p.Modes.state_detection_mode

        if qubit == 'qubit_0':
            self.pi_time = self.p.Pi_times.qubit_0

        elif qubit == 'qubit_plus':
            self.pi_time = self.p.Pi_times.qubit_plus

        elif qubit == 'qubit_minus':
            self.pi_time = self.p.Pi_times.qubit_minus

        init_bright_state_pumping_method = self.p.BrightStatePumping.method
        init_microwave_pulse_sequence = self.p.MicrowaveInterogation.pulse_sequence
        init_optical_pumping_method = self.p.OpticalPumping.method

        self.p['MicrowaveInterogation.pulse_sequence'] = 'standard'

        line_trigger = self.p.MicrowaveInterogation.AC_line_trigger
        if line_trigger == 'On':
            self.pulser.line_trigger_state(True)

        self.setup_datavault('time', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Rabi Point Tracker')
        self.n_pi_times = self.p.RabiPointTracker.number_pi_times
        init_time = U(time.time(), 's')
        i = 0
        while True:
            print(self.pi_time)
            should_break = self.update_progress(np.random.rand())
            if should_break:
                break
            if mode == 'Standard':
                # force standard optical pumping if standard readout method used
                # no sense in quadrupole optical pumping by accident if using standard readout
                self.p['OpticalPumping.method'] = 'Standard'

            self.p['MicrowaveInterogation.duration'] = self.n_pi_times * self.pi_time
            self.program_pulser(sequence)

            if mode == 'Shelving':
                [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
                errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                counts = np.delete(detection_counts, errors)
            elif mode == 'Standard':
                [counts] = self.run_sequence()
            else:
                print 'Detection mode not selected!!!'

            time_since_start = U(time.time(), 's') - init_time

            if i % self.p.StandardStateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                # only plot the histogram if you're not in the middle of drift tracking
                # during a shelving fidelity run
                if self.p.RabiPointTracker.shelving_fidelity_drift_tracking == 'OFF':
                    self.plot_hist(hist)

            pop = self.get_pop(counts)
            # if we are drift tracking during a shelving fidelity run we want to return
            # the measured pop to the shelving fidelity experiment so it can make a decision
            # based on the observed population
            if self.p.RabiPointTracker.shelving_fidelity_drift_tracking == 'ON':
                return pop

            if self.p.RabiPointTracker.pi_time_feedback == 'ON':
                self.update_pi_time(pop, gain=0.1)

            self.dv.add(time_since_start['s'], pop)
            i +=1

        self.p['BrightStatePumping.method'] = init_bright_state_pumping_method
        self.p['MicrowaveInterogation.pulse_sequence'] = init_microwave_pulse_sequence
        self.p['OpticalPumping.method'] = init_optical_pumping_method
        self.pulser.line_trigger_state(False)

    def update_pi_time(self, pop, gain, set_point=0.5):
        error = (pop - set_point)
        if np.abs(error) > 0.05:
            self.pi_time = self.pi_time - gain*error*self.pi_time/self.n_pi_times
        else:
            self.pi_time = self.pi_time

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveRabiFlopping(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
