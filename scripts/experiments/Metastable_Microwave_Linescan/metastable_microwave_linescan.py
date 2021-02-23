import labrad
from Qsim.scripts.pulse_sequences.metastable_microwave_point import metastable_microwave_point as sequence
from Qsim.scripts.pulse_sequences.heralded_metastable_microwave_point import heralded_metastable_microwave_point as heralded_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MetastableMicrowaveLineScan(QsimExperiment):
    """
    Scan 3.6 GHz microwave source over the qubit transition in the F7/2
    state. There are different ways of running this experiment as well,
    like with heralded state preparation or not
    """

    name = 'Metastable Microwave Line Scan'

    exp_parameters = []
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))
    exp_parameters.append(('MetastableMicrowaveLinescan', 'scan'))
    exp_parameters.append(('Pi_times', 'metastable_qubit'))
    exp_parameters.append(('Line_Selection', 'qubit'))
    exp_parameters.append(('Pi_times', 'qubit_0'))
    exp_parameters.append(('Pi_times', 'qubit_plus'))
    exp_parameters.append(('Pi_times', 'qubit_minus'))

    exp_parameters.extend(sequence.all_required_parameters())

    # exp_parameters.remove(('MicrowaveInterogation', 'detuning'))
    # exp_parameters.remove(('MicrowaveInterogation', 'duration'))
    # exp_parameters.remove(('MetastableMicrowaveInterogation', 'detuning'))
    # exp_parameters.remove(('MetastableMicrowaveInterogation', 'duration'))

    exp_parameters.append(('MetastableStateDetection', 'repetitions'))
    exp_parameters.append(('MetastableStateDetection', 'herald_state_prep'))
    exp_parameters.append(('HeraldedStatePreparation', 'deshelving_duration'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('frequency', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Metastable Microwave Linescan')
        self.detunings = self.get_scan_list(self.p.MetastableMicrowaveLinescan.scan, 'kHz')

        qubit = self.p.Line_Selection.qubit
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
        self.p['Metastable_Microwave_Interrogation.duration'] = self.p.Pi_times.metastable_qubit
        self.p['Modes.state_detection_mode'] = 'Shelving'

        print(self.p['Metastable_Microwave_Interrogation.duration'])

        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i/float(len(self.detunings)))
            if should_break:
                break
            self.p['Metastable_Microwave_Interrogation.detuning'] = U(detuning, 'kHz')
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
                # this will combine all errors into one array and delete repeats (error on both doppler and herald)
                all_errors = np.unique(np.concatenate((failed_heralding[0], doppler_errors[0])))
                counts = np.delete(detection_counts, all_errors)
                print len(counts)

            hist = self.process_data(counts)
            self.plot_hist(hist)
            pop = self.get_pop(counts)

            self.dv.add(detuning + self.p.Transitions.MetastableQubit['kHz'], pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MetastableMicrowaveLineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
