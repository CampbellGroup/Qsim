import labrad
from Qsim.scripts.pulse_sequences.metastable_microwave_point import metastable_microwave_point as sequence
from Qsim.scripts.pulse_sequences.heralded_metastable_microwave_point import heralded_metastable_microwave_point as heralded_sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np


class MetastableMicrowaveRabiFlopping(QsimExperiment):
    """
    Scan the interrogation time of the 3.6 GHz radiation for the
    metastable qubit. Can perform heralded state preparation if desired
    """

    name = 'Metastable Microwave Rabi Flopping'

    exp_parameters = []
    exp_parameters.append(('MetastableMicrowaveRabiFlopping', 'scan'))
    exp_parameters.append(('DopplerCooling', 'detuning'))
    exp_parameters.append(('Transitions', 'main_cooling_369'))

    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('ShelvingStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('Shelving_Doppler_Cooling', 'doppler_counts_threshold'))
    exp_parameters.append(('HeraldedStatePreparation', 'deshelving_duration'))
    exp_parameters.append(('MetastableStateDetection', 'herald_state_prep'))
    exp_parameters.append(('Pi_times', 'metastable_qubit'))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(('Metastable_Microwave_Interrogation', 'duration'))

    def initialize(self, cxn, context, ident):
        self.ident = ident

    def run(self, cxn, context):

        self.setup_datavault('time', 'probability')  # gives the x and y names to Data Vault
        self.setup_grapher('Metastable Qubit Rabi Flopping')

        self.p['Line_Selection.qubit'] = 'qubit_0'  # define the bright state prep as qubit_0
        self.p['Modes.state_detection_mode'] = 'Shelving'
        self.p['MicrowaveInterrogation.duration'] = self.p.Pi_times.qubit_0

        self.times = self.get_scan_list(self.p.MetastableMicrowaveRabiFlopping.scan, 'us')
        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i/float(len(self.times)))
            if should_break:
                break
            self.p['Metastable_Microwave_Interrogation.duration'] = U(duration, 'us')
#            self.program_pulser(sequence)
#            [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
#            errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
#            counts = np.delete(detection_counts, errors)
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
            self.dv.add(duration, pop)

    def finalize(self, cxn, context):
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MetastableMicrowaveRabiFlopping(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
