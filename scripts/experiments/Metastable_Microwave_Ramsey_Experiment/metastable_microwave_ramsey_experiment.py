import labrad
from Qsim.scripts.pulse_sequences.metastable_microwave_ramsey_point import metastable_microwave_ramsey_point as sequence
from Qsim.scripts.pulse_sequences.heralded_metastable_microwave_ramsey_point import heralded_metastable_microwave_ramsey_point as heralded_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MetastableMicrowaveRamseyExperiment(QsimExperiment):
    """

    """

    name = 'Metastable Microwave Ramsey Experiment'

    exp_parameters = []
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('MetastableStateDetection', 'herald_state_prep'))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.extend(heralded_sequence.all_required_parameters())

    exp_parameters.remove(('EmptySequence', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.heralded_number_experiments = []

    def run(self, cxn, context):

        self.p['Line_Selection.qubit'] = 'qubit_0'  # define the bright state prep as qubit_0
        self.p['Modes.state_detection_mode'] = 'Shelving'

        if self.p.Shelving.assist_laser == 'Doppler Cooling':
            self.p['MicrowaveInterrogation.duration'] = self.p.Pi_times.qubit_0
            self.p['MicrowaveInterrogation.repetitions'] = 1.0
        elif self.p.Shelving.assist_laser == 'Optical Pumping':
            self.p['MicrowaveInterrogation.repetitions'] = 0.0

        scan_parameter = self.p.MetastableMicrowaveRamsey.scan_type

        if scan_parameter == "delay_time":
            self.setup_datavault('time', 'probability')  # gives the x and y names to Data Vault
            self.setup_grapher('Metastable Microwave Ramsey Experiment')
            self.dark_time = self.get_scan_list(self.p.MetastableMicrowaveRamsey.delay_time, 'ms')
            for i, dark_time in enumerate(self.dark_time):
                should_break = self.update_progress(i/float(len(self.dark_time)))
                if should_break:
                    break
                self.p['EmptySequence.duration'] = U(dark_time, 'ms')

                if self.p.MetastableStateDetection.herald_state_prep == 'Off':
                    self.program_pulser(sequence)
                    [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
                    errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                    counts = np.delete(detection_counts, errors)

                if self.p.MetastableStateDetection.herald_state_prep == 'On':
                    self.program_pulser(heralded_sequence)
                    [doppler_counts, herald_counts, detection_counts] = self.run_sequence(max_runs=333, num=3)
                    failed_heralding = np.where(herald_counts >= self.p.ShelvingStateDetection.state_readout_threshold)
                    doppler_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                    all_errors = np.unique(np.concatenate((failed_heralding[0], doppler_errors[0])))
                    counts = np.delete(detection_counts, all_errors)
                    self.heralded_number_experiments.append(len(counts))

                print(self.heralded_number_experiments)
                hist = self.process_data(counts)
                self.plot_hist(hist)
                pop = self.get_pop(counts)
                self.dv.add(dark_time, pop)

        elif scan_parameter == "phase":
            self.setup_datavault('phase', 'probability')
            self.setup_grapher('Metastable Microwave Ramsey Experiment')
            self.phase_list = self.get_scan_list(self.p.MetastableMicrowaveRamsey.phase_scan, 'deg')
            self.p['EmptySequence.duration'] = self.p.MetastableMicrowaveRamsey.fixed_delay_time
            self.p['MetastableMicrowaveRamsey.detuning'] = U(0.0, 'kHz')
            for i, phase in enumerate(self.phase_list):
                should_break = self.update_progress(i/float(len(self.phase_list)))
                if should_break:
                    break
                self.p['Metastable_Microwave_Interrogation.microwave_phase'] = U(phase, 'deg')

                if self.p.MetastableStateDetection.herald_state_prep == 'Off':
                    self.program_pulser(sequence)
                    [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
                    errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                    counts = np.delete(detection_counts, errors)

                if self.p.MetastableStateDetection.herald_state_prep == 'On':
                    self.program_pulser(heralded_sequence)
                    [doppler_counts, herald_counts, detection_counts] = self.run_sequence(max_runs=333, num=3)
                    failed_heralding = np.where(herald_counts >= self.p.ShelvingStateDetection.state_readout_threshold)
                    doppler_errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                    all_errors = np.unique(np.concatenate((failed_heralding[0], doppler_errors[0])))
                    counts = np.delete(detection_counts, all_errors)
                    self.heralded_number_experiments.append(len(counts))

                print(self.heralded_number_experiments)
                hist = self.process_data(counts)
                self.plot_hist(hist)
                pop = self.get_pop(counts)
                print phase, pop
                self.dv.add(phase, pop)


    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MetastableMicrowaveRamseyExperiment(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
