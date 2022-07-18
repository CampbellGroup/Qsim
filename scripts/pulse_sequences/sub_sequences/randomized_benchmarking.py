import numpy as np
from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import pulse_sequence

from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_X import clifford_X
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_minus_X import clifford_minus_X
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_Y import clifford_Y
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_minus_Y import clifford_minus_Y
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_Z import clifford_Z

from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_X import pauli_X
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_minus_X import pauli_minus_X
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_Y import pauli_Y
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_minus_Y import pauli_minus_Y
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_Id import pauli_Id
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.single_sequence_rb_testing import single_sequence_rb_testing


class randomized_benchmarking_pulse(pulse_sequence):

    required_parameters = [
        ('RandomizedBenchmarking', 'file_selection'),
        ('MicrowaveInterrogation', 'power'),
        ('MicrowaveInterrogation', 'ttl_switch_delay'),
        ('Line_Selection', 'qubit'),
        ('Transitions', 'qubit_0'),
        ('ddsDefaults', 'qubit_dds_freq'),
        ('Pi_times', 'qubit_0'),
                           ]

    required_subsequences = [
        clifford_X,
        clifford_minus_X,
        clifford_Y,
        clifford_minus_Y,
        clifford_Z,
        pauli_X,
        pauli_minus_X,
        pauli_Y,
        pauli_minus_Y,
        pauli_Id,
        single_sequence_rb_testing
    ]

    def sequence(self):
        p = self.parameters

        pulse_dict = {'[0.0, 0.5, 1.0]': clifford_X,
                      '[180.0, 0.5, 1.0]': clifford_minus_X,
                      '[90.0, 0.5, 1.0]': clifford_Y,
                      '[270.0, 0.5, 1.0]': clifford_minus_Y,
                      '[0.0, 1.0, 1.0]': pauli_X,
                      '[180.0, 1.0, 1.0]': pauli_minus_X,
                      '[90.0, 1.0, 1.0]': pauli_Y,
                      '[270.0, 1.0, 1.0]': pauli_minus_Y,
                      '[0.0, 1.0, 0.0]': pauli_Id,
                      '[0.0, 0.5, 0.0]': clifford_Z}

        # gets the file with the pulse sequence
        rb_pulses = np.loadtxt(p.RandomizedBenchmarking.file_selection, delimiter=',')
        # num_reps = 10
        # for i in range(num_reps):
        #     self.addSequence(single_sequence_rb_testing)
        for pulse in rb_pulses:
            self.addSequence(pulse_dict[str(list(pulse))])
