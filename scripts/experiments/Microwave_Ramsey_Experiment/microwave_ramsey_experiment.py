import labrad
from Qsim.scripts.pulse_sequences.microwave_ramsey_point import microwave_ramsey_point as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MicrowaveRamseyExperiment(QsimExperiment):
    """
    Scan delay time between microwave pulses with variable pulse area
    """

    name = 'Microwave Ramsey Experiment'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('MicrowaveInterrogation', 'detuning'))
    exp_parameters.append(('MicrowaveRamsey', 'delay_time'))
    exp_parameters.append(('MicrowaveRamsey', 'fixed_delay_time'))
    exp_parameters.append(('MicrowaveRamsey', 'detuning'))
    exp_parameters.append(('MicrowaveRamsey', 'scan_type'))
    exp_parameters.append(('MicrowaveRamsey', 'phase_scan'))
    exp_parameters.append(('MicrowaveInterrogation', 'AC_line_trigger'))
    exp_parameters.append(('MicrowaveInterrogation', 'delay_from_line_trigger'))
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('EmptySequence', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        if self.p.MicrowaveInterrogation.AC_line_trigger == 'On':
            self.pulser.line_trigger_state(True)
            self.pulser.line_trigger_duration(self.p.MicrowaveInterrogation.delay_from_line_trigger)

        scan_parameter = self.p.MicrowaveRamsey.scan_type
        mode = self.p.Modes.state_detection_mode

        qubit = self.p.Line_Selection.qubit
        if qubit == 'qubit_0':
            pi_time = self.p.Pi_times.qubit_0

        elif qubit == 'qubit_plus':
            pi_time = self.p.Pi_times.qubit_plus

        elif qubit == 'qubit_minus':
            pi_time = self.p.Pi_times.qubit_minus

        self.p['MicrowaveInterrogation.detuning'] = self.p.MicrowaveRamsey.detuning

        if scan_parameter == "delay_time":
            self.setup_datavault('time', 'probability')  # gives the x and y names to Data Vault
            self.setup_grapher('Microwave Ramsey Experiment')
            self.dark_time = self.get_scan_list(self.p.MicrowaveRamsey.delay_time, 'ms')
            for i, dark_time in enumerate(self.dark_time):
                should_break = self.update_progress(i/float(len(self.dark_time)))
                if should_break:
                    break
                self.p['EmptySequence.duration'] = U(dark_time, 'ms')
                self.program_pulser(sequence)
                if mode == 'Shelving':
                    [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
                    errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                    counts = np.delete(detection_counts, errors)
                else:
                    [counts] = self.run_sequence()
                if i % self.p.StandardStateDetection.points_per_histogram == 0:
                    hist = self.process_data(counts)
                    self.plot_hist(hist)
                pop = self.get_pop(counts)
                self.dv.add(dark_time, pop)

        elif scan_parameter == "phase":
            self.setup_datavault('phase', 'probability')
            self.setup_grapher('Microwave Ramsey Experiment')
            self.phase_list = self.get_scan_list(self.p.MicrowaveRamsey.phase_scan, 'deg')
            self.p['EmptySequence.duration'] = self.p.MicrowaveRamsey.fixed_delay_time
            print(str(self.p.MicrowaveRamsey.fixed_delay_time))
            for i, phase in enumerate(self.phase_list):
                should_break = self.update_progress(i/float(len(self.phase_list)))
                if should_break:
                    break
                self.p['MicrowaveInterrogation.microwave_phase'] = U(phase, 'deg')
                self.program_pulser(sequence)
                if mode == 'Shelving':
                    [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
                    errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                    counts = np.delete(detection_counts, errors)
                else:
                    [counts] = self.run_sequence()
                if i % self.p.StandardStateDetection.points_per_histogram == 0:
                    hist = self.process_data(counts)
                    self.plot_hist(hist)
                pop = self.get_pop(counts)
                print(len(counts))
                print(str(phase) + ' deg , ' + str(pop) + 'population')
                self.dv.add(phase, pop)

    def finalize(self, cxn, context):
        self.pulser.line_trigger_state(False)
        self.pulser.line_trigger_duration(U(0.0, 'us'))
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveRamseyExperiment(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
