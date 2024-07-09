import numpy as np
from common.lib.servers.Pulser2.pulse_sequences.pulse_sequence import PulseSequence

from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_X import CliffordX
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_minus_X import CliffordMinusX
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_Y import CliffordY
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_minus_Y import CliffordMinusY
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.clifford_Z import CliffordZ

from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_X import PauliX
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_minus_X import PauliMinusX
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_Y import PauliY
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_minus_Y import PauliMinusY
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.pauli_Id import PauliId
from Qsim.scripts.pulse_sequences.sub_sequences.single_qubit_gates.single_sequence_rb_testing import SingleSequenceRbTesting


class RandomizedBenchmarkingPulse(PulseSequence):

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
        CliffordX,
        CliffordMinusX,
        CliffordY,
        CliffordMinusY,
        CliffordZ,
        PauliX,
        PauliMinusX,
        PauliY,
        PauliMinusY,
        PauliId,
        SingleSequenceRbTesting
    ]

    def sequence(self):
        p = self.parameters

        pulse_dict = {'[0.0, 0.5, 1.0]': CliffordX,
                      '[180.0, 0.5, 1.0]': CliffordMinusX,
                      '[90.0, 0.5, 1.0]': CliffordY,
                      '[270.0, 0.5, 1.0]': CliffordMinusY,
                      '[0.0, 1.0, 1.0]': PauliX,
                      '[180.0, 1.0, 1.0]': PauliMinusX,
                      '[90.0, 1.0, 1.0]': PauliY,
                      '[270.0, 1.0, 1.0]': PauliMinusY,
                      '[0.0, 1.0, 0.0]': PauliId,
                      '[0.0, 0.5, 0.0]': CliffordZ}

        # gets the file with the pulse sequence
        rb_pulses = np.loadtxt(p.RandomizedBenchmarking.file_selection, delimiter=',')
        # num_reps = 10
        # for i in range(num_reps):
        #     self.addSequence(single_sequence_rb_testing)
        for pulse in rb_pulses:
            self.add_sequence(pulse_dict[str(list(pulse))])
