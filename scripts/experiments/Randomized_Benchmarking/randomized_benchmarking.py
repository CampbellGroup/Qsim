import os
import labrad
import numpy as np
import random as random
from labrad.units import WithUnit as U
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import Qsim.scripts.experiments.Randomized_Benchmarking.generate_save_rb_sequences as generate_sequences
from Qsim.scripts.pulse_sequences.randomized_benchmarking import randomized_benchmarking as sequence


class RandomizedBenchmarking(QsimExperiment):
    """
    repeatedly prepare the |0> state, performing a random RB sequence N_e times and detecting the final state.
    """

    name = 'Randomized Benchmarking'

    exp_parameters = []
    exp_parameters.append(('Modes', 'state_detection_mode'))
    exp_parameters.append(('ShelvingStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'repetitions'))
    exp_parameters.append(('StandardStateDetection', 'points_per_histogram'))
    exp_parameters.append(('StandardStateDetection', 'state_readout_threshold'))
    exp_parameters.append(('RandomizedBenchmarking', 'sequence_generation'))
    exp_parameters.append(('RandomizedBenchmarking', 'set_of_lengths'))
    exp_parameters.append(('RandomizedBenchmarking', 'file_selection'))
    exp_parameters.append(('RandomizedBenchmarking', 'clifford_sequences'))
    exp_parameters.append(('RandomizedBenchmarking', 'pauli_randomizations'))
    exp_parameters.append(('MicrowaveInterrogation', 'AC_line_trigger'))
    exp_parameters.extend(sequence.all_required_parameters())

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser

    def run(self, cxn, context):
        # if we want to line trigger tell the pulser to do so
        self.pulser.line_trigger_state(self.p.MicrowaveInterrogation.AC_line_trigger == 'On')

        sets = []
        # put path to the files here
        path_to_files = '/home/qsimexpcontrol/LabRAD/Qsim/scripts/experiments/Randomized_Benchmarking/RB_Sequences/'
        for i in os.listdir(path_to_files):
            sets.append(int(i.split('_')[2]))
        sequences = []
        #print(max(sets))
        if self.p.RandomizedBenchmarking.sequence_generation == 'Use Most Recent Set':
            path = path_to_files + 'Sequence_Set_' + str(max(sets))
            expected_outcomes = np.loadtxt(path + '/Sequence_Final_States.csv', delimiter=',', dtype=np.str)
            for i in os.listdir(path):
                sequences.append(i)

        elif self.p.RandomizedBenchmarking.sequence_generation == 'Generate New Set':
            path = path_to_files + 'Sequence_Set_' + str(max(sets) + 1)
            lengths = [int(i) for i in self.p.RandomizedBenchmarking.set_of_lengths.split(',')]
            print('Generating new RB sequence... please hold.')
            generate_sequences.generate_and_save_sequences(lengths,
                                                      int(self.p.RandomizedBenchmarking.clifford_sequences),
                                                      int(self.p.RandomizedBenchmarking.pauli_randomizations),
                                                      path)
            expected_outcomes = np.loadtxt(path + '/Sequence_Final_States.csv', delimiter=',', dtype=np.str)
            print('New sequence has been generated')
            for i in os.listdir(path):
                sequences.append(i)

        sequences.remove('Sequence_Final_States.csv')
        mode = self.p.Modes.state_detection_mode

        # These 3 lines need to change for rb
        self.setup_datavault('sequence_length', 'probability')  # gives the x and y names to Data Vault

        self.setup_grapher('Randomized Benchmarking')
        total_number_sequences = len(sequences)
        np.random.shuffle(sequences)
        #print(self.p.Pi_times.qubit_0['us'])
        #print(self.p.MicrowaveInterrogation.ttl_switch_delay['us'])
        #print(self.p.Transitions.qubit_0['kHz'])
        for i in range(len(sequences)):
            should_break = self.update_progress(i/float(total_number_sequences))
            if should_break:
                break

            rb_sequence = sequences[i]
            rb_sequence_label = rb_sequence[9:-4]
            clifford_length = float(rb_sequence_label.split('_')[0])
            #outcome = 1
            outcome = float(expected_outcomes[np.where(expected_outcomes[:, 0] == rb_sequence_label)[0]][0][1])

            self.p['RandomizedBenchmarking.file_selection'] = path + '/' + rb_sequence
            self.program_pulser(sequence)

            if mode == 'Shelving':
                [doppler_counts, detection_counts] = self.run_sequence(max_runs=500, num=2)
                errors = np.where(doppler_counts <= self.p.Shelving_Doppler_Cooling.doppler_counts_threshold)
                counts = np.delete(detection_counts, errors)
            elif mode == 'Standard':
                [counts] = self.run_sequence(max_runs=1000, num=1)

            if i % self.p.StandardStateDetection.points_per_histogram == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)


            pop = self.get_pop(counts)

            if mode == 'Standard':
                fid = (1.0 - (-1.0)**(outcome) * pop) - outcome

            if fid < 0.85:
                print(rb_sequence_label)

            self.dv.add(clifford_length, fid)

    '''
    def setup_datavault(self):
        self.rb_context = self.dv.context()

        self.dv.cd(['', 'Randomized_Benchmarking'],
                   True, context=self.rb_context)

        self.rb_dataset = self.dv.new('randomized_benchmarking', [('run', 'arb')], [('length', 'clifford_length', 'num'),
                                                                                    ('pop', 'prob', 'num'),
                                                                                    ('expected_outcome', 'state', 'num')], context=self.rb_context)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter],
                                  context=self.rb_context)

        self.rb_fid_context = self.dv.context()

        self.dv.cd(['', 'Randomized_Benchmarking'],
                   True, context=self.rb_fid_context)

        self.rb_dataset = self.dv.new('randomized_benchmarking_fid', [('run', 'arb')],
                                      [('length', 'clifford_length', 'num'),
                                       ('fid', 'prob', 'num')
                                       ], context=self.rb_fid_context)
    
    '''

    def finalize(self, cxn, context):
        self.pulser.line_trigger_state(False)
        pass


if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = RandomizedBenchmarking(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
