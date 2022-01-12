import os as os
import numpy as np
import qutip as qt
import random as random

def generate_gate_sequence(sequence_length, gate_type):
    """Creates a Clifford or Pauli gate sequence given a length
    Returns: a list of strings which are random clifford or pauli gates
    Takes: sequence_length: (int) how long you want the sequence to be
           gate_type: (str) 'pauli' or 'clifford' depending on which gates to pull from
    """
    paulis = [['x', 1, np.pi], ['x', -1, np.pi],
              ['y', 1, np.pi], ['y', -1, np.pi],
              ['z', 1, np.pi], ['z', -1, np.pi],
              ['i', 1, np.pi], ['i', -1, np.pi]]

    cliffords = [['x', 1, np.pi / 2.], ['x', -1, np.pi / 2.],
                 ['y', 1, np.pi / 2.], ['y', -1, np.pi / 2.]]

    gate_sequence = []
    for i in range(sequence_length):
        if gate_type == 'clifford':
            gate_sequence.append(random.choice(cliffords))
        elif gate_type == 'pauli':
            gate_sequence.append(random.choice(paulis))

    return gate_sequence


def make_gate(gate_information):
    """Creates a gate based on a string containing all the gate information
    Returns: a numpy array (matrix) which can act on a state vector to obtain the rotated state
    Takes: gate_information: a list of the form: ['axis', sign, pulse_area] (types: [str, int, float])
           sigma_z_state: 1 or -1 depending on the number of sigmaz gates performed prior to the gate being made
    """
    gate_type = gate_information[0]
    gate_sign = gate_information[1]
    pulse_area = gate_information[2]

    if gate_type == 'x':
        matrix = qt.sigmax()
    elif gate_type == 'y':
        matrix = qt.sigmay()
    elif gate_type == 'z':
        matrix = qt.sigmaz()
    elif gate_type == 'i':
        matrix = qt.qeye(2)
    else:
        matrix = qt.qeye(2)
        print('Gate type not of typical format, using identity.')

    operator = gate_sign * 1.j * matrix * pulse_area / 2.
    return operator.expm()


def find_last_gate(gate_sequence, initial_state):
    """Finds the two gates which will result in an eigenstate of z and then randomly picks one of those two gates.
    Then applies a Pauli at random
    Returns: A final gate list which includes the randomly chosen final gate (clifford + pauli)
             The expected final state
    Takes: A list of gates
           The initial state
    """
    final_cliffords = {'z': [qt.sigmaz(), [['z', 1, np.pi / 2], ['z', -1, np.pi / 2]]],
                       'x': [qt.sigmax(), [['y', 1, np.pi / 2], ['y', -1, np.pi / 2]]],
                       'y': [qt.sigmay(), [['x', 1, np.pi / 2], ['x', -1, np.pi / 2]]]}

    final_paulis = [['x', 1, np.pi], ['x', -1, np.pi],
                    ['y', 1, np.pi], ['y', -1, np.pi],
                    ['z', 1, np.pi], ['z', -1, np.pi],
                    ['i', 1, np.pi], ['i', -1, np.pi]]



    final_sequence = gate_sequence
    state = initial_state
    for gate in gate_sequence:
        state = make_gate(gate) * state

    for sigma in final_cliffords:
        if final_cliffords[sigma][0] * state == state or final_cliffords[sigma][0] * state == -1 * state:
            final_clifford = random.choice(final_cliffords[sigma][1])
            final_sequence.append(final_clifford)
            state = make_gate(final_clifford) * state
            state = qt.Qobj([[state[0][0][0] * state[0][0][0].conj()], [state[1][0][0] * state[1][0][0].conj()]])
            break

    last_pauli = random.choice(final_paulis)

    if last_pauli[0] == 'x' or 'y':
        if final_clifford[0] == 'z':
            if final_clifford[1] == 1:
                if last_pauli[0] == 'x' and last_pauli[1] == 1:
                    last_pauli[0] = 'y'
                elif last_pauli[0] == 'y' and last_pauli[1] == 1:
                    last_pauli[0] = 'x'
                    last_pauli[1] = -1
                elif last_pauli[0] == 'x' and last_pauli[1] == -1:
                    last_pauli[0] = 'y'
                elif last_pauli[0] == 'y' and last_pauli[1] == -1:
                    last_pauli[0] = 'x'
                    last_pauli[1] = 1
            elif final_clifford[1] == -1:
                if last_pauli[0] == 'x' and last_pauli[1] == 1:
                    last_pauli[0] = 'y'
                    last_pauli[1] = -1
                elif last_pauli[0] == 'y' and last_pauli[1] == 1:
                    last_pauli[0] = 'x'
                elif last_pauli[0] == 'x' and last_pauli[1] == -1:
                    last_pauli[0] = 'y'
                    last_pauli[1] = 1
                elif last_pauli[0] == 'y' and last_pauli[1] == -1:
                    last_pauli[0] = 'x'

    state = make_gate(last_pauli) * state
    expected_final_state = qt.Qobj(
        [[state[0][0][0] * state[0][0][0].conj()], [state[1][0][0] * state[1][0][0].conj()]])
    final_sequence.append(last_pauli)

    return final_sequence, expected_final_state


def generate_microwave_rotation_matrix(omega, delta, t, phi):
    """Takes: omega: the resonant rabi frequency
           delta: detuning from the resonant frequency
           t: duration of the microwave pulse
           phi: the relative phase of the pulse
    Returns: a numpy array (2x2) which is the rotation matrix for the microwave pulse
    """
    omega_R = np.sqrt(omega ** 2. + delta ** 2.)
    rotation_matrix = np.array([[np.cos(omega_R * t / 2.) + (1.j * delta / omega_R) * np.sin(omega_R * t / 2.),
                                 (-1.j * omega / omega_R) * np.sin(omega_R * t / 2.) * np.exp(-1.j * phi)],
                                [(-1.j * omega / omega_R) * np.sin(omega_R * t / 2.) * np.exp(1.j * phi),
                                 np.cos(omega_R * t / 2.) - (1j * delta / omega_R) * np.sin(omega_R * t / 2.)]])
    return rotation_matrix


def generate_free_qubit_evolution(delta, t):
    """Generates a free qubit rotation in the oscillator frame for given detuning and time
    Takes: delta: (float): detuning from resonance (2pi needed)
           t: (float): time to evolve
    Returns: qubit_evolution_matrix: (np array) 2x2 numpy array which will evolve the qubit state
    """
    qubit_evolution_matrix = np.array([[np.exp(1j * delta * t / 2),
                                        0],
                                       [0,
                                        np.exp(-1j * delta * t / 2)]])
    return qubit_evolution_matrix


def generate_interleaved_gate_sequence(clifford_gate_sequence, pauli_gate_sequence):
    """Interleaves given clifford and pauli randomizer sequences.
    Returns: final_gate_sequence: list of all gates (Pauli and Clifford) to apply.
    Takes: clifford_gate_sequence: list of all clifford gates in order
           pauli_gate_sequence: list of all pauli gates in order
    """
    final_gate_sequence = []
    for i in range(len(clifford_gate_sequence)):
        final_gate_sequence.append(pauli_gate_sequence[i])
        final_gate_sequence.append(clifford_gate_sequence[i])
    final_gate_sequence.append(pauli_gate_sequence[-1])
    return final_gate_sequence


def insert_delay_gate_sequence(gate_sequence, delay_time, omega):
    """Interleaves given delay time in between all pulses.
    Returns: final_gate_sequence: list of all gates (Pauli, Clifford, and delays) to apply.
    Takes: gate_sequence: list of all gates in order
           delay_time: time to wait between pulses
           omega: Rabi time in order to calculate pulse area (2pi needed)
    """
    final_gate_sequence = []
    delay_gate = ['i', 1, delay_time * omega]
    for i in range(len(gate_sequence) - 1):
        final_gate_sequence.append(gate_sequence[i])
        final_gate_sequence.append(delay_gate)
    final_gate_sequence.append(gate_sequence[-1])
    return final_gate_sequence


def changing_pauli_frame_sequence(gate_sequence):
    """Tracks the z axis pauli gates to determine the phase of all subsequent gates (change of Pauli frame). Replaces
    all z gates with I.
    Takes: gate_sequence: (list of lists): pulse sequence to track all z gates [(str): gate type, (int) gate sign,
                                                                                (float) pulse area]
    Returns: useable_sequence: (list of lists): updated pulse sequence when the Pauli frame is rotated to account for
                                                the z gates [(str): gate type, (int) gate sign, (float) pulse area]
    """
    sign = 1
    useable_sequence = []
    for gate in gate_sequence:
        if gate[0] == 'z':
            sign *= -1
            new_gate = ['i', 1, gate[2]]
            useable_sequence.append(new_gate)
        else:
            new_gate = [gate[0], gate[1] * sign, gate[2]]
            useable_sequence.append(new_gate)

    return useable_sequence


def rbm_model_experiment(initial_state, expected_final_state, final_gate_sequence):
    """Performs a simulated randomized benchmarking experiment with perfect pulses, unaware of any frequency information.
    Takes: initial_state: (qutip object): 2x1 qutip object of the initial state
           expected_final_state: (qutip object) 2x1 qutip object of the expected final state
           final_gate_sequence: (list of lists) pulse sequence to use [(str): gate type, (int) gate sign, (float) pulse area]
    Returns: final_state: (qutip object) 2x1 qutip object of the found final state
    """
    state = initial_state
    for gate in final_gate_sequence:
        state = make_gate(gate) * state
    final_state = qt.Qobj([[state[0][0][0] * state[0][0][0].conj()], [state[1][0][0] * state[1][0][0].conj()]])

    match = 0
    miss = 0
    if final_state == expected_final_state:
        match += 1
        # print('All good in the hood!')
    else:
        miss += 1
        print('DANGER DANGER')
    return final_state


def rbm_real_experiment(initial_state, gate_sequence, omega, delta):
    """Performs a simulated randomized benchmarkng experiment given a pulse sequence, the initial state, a rabi frequency and the detuning.
    Takes: initial_state: (np array) a 2x1 array of the initial state.
           gate_sequence: (list of lists) contains all gate information needed [microwave state (bool), phase (float), pulse area (float)]
           omega: (float) the resonant Rabi frequency (2pi required)
           delta: (float) detuning from resonance
    Returns: state: (np array) a 2x1 array of the final state
    """
    state = initial_state
    rabi_freq = omega
    for gate in gate_sequence:
        if gate[0] == False:
            rotation = generate_free_qubit_evolution(delta, gate[2] * np.pi / omega)
            state = np.dot(rotation, state)
        elif gate[0] == True:
            rotation = generate_microwave_rotation_matrix(rabi_freq, delta, gate[2] * np.pi / omega,
                                                          np.radians(gate[1]))
            state = np.dot(rotation, state)
    return state


def gate_to_experiment_params(gate_sequence):
    """Takes a gate sequence generated of the form ['G_i', sign, pulse area], and turns it into useable experimental parameters
    Returns: experiment_sequence: (list of lists) [microwave state (Boolean), phase (float), pulse area (float)]
    Takes: gate_sequence: (list of lists) [gate type (string), gate sign (int), pulse area (float)]
    """
    experiment_sequence = []
    for gate in gate_sequence:
        if gate[0] == 'x':
            if gate[1] == 1:
                phi = 0.
            elif gate[1] == -1:
                phi = 180.
            microwaves_on = True
        elif gate[0] == 'y':
            if gate[1] == 1:
                phi = 90.
            elif gate[1] == -1:
                phi = 270.
            microwaves_on = True
        else:
            microwaves_on = False
            phi = 0.
        if gate[2] == np.pi:
            pulse_area = 1.
        elif gate[2] == np.pi / 2.:
            pulse_area = 1 / 2.

        experiment_sequence.append([microwaves_on, phi, pulse_area])

    return experiment_sequence


def generate_and_save_sequences(lengths, number_of_gate_sequences, number_of_pauli_randomizations, path):
    # If it can't find the directory, make it and make the first directory for the sequences
    # for actually running this, you're only going to call this file if you need to generate sequences.

    '''
    if not os.path.isdir('RBM_Pulse_Sequences'):
        os.makedirs('RBM_Pulse_Sequences/Sequence_Set_1')
        path = 'RBM_Pulse_Sequences/Sequence_Set_1'
    else:
        sets = []
        for i in os.listdir('RBM_Pulse_Sequences/'):
            sets.append(int(i.split('_')[2]))
        os.makedirs('RBM_Pulse_Sequences/Sequence_Set_' + str(max(sets) + 1))
        path = 'RBM_Pulse_Sequences/Sequence_Set_' + str(max(sets) + 1)
    '''
    os.makedirs(path)
    initial_state = qt.Qobj([[1], [0]])
    with open(path + '/Sequence_Final_States.csv', 'w') as states_file:
        for i in range(number_of_gate_sequences):
            clifford_sequence = generate_gate_sequence(max(lengths) - 1, 'clifford')
            for j in lengths:
                trunc_clifford_sequence = clifford_sequence[:j - 1]
                for k in range(number_of_pauli_randomizations):
                    pauli_randomizer_sequence = generate_gate_sequence(len(trunc_clifford_sequence) + 1, 'pauli')
                    interleaved_gate_sequence = generate_interleaved_gate_sequence(trunc_clifford_sequence,
                                                                                   pauli_randomizer_sequence)
                    final_gate_sequence, expected_final_state = find_last_gate(interleaved_gate_sequence, initial_state)
                    expected_final_state_real = np.array([np.real([expected_final_state[0][0][0]]),
                                                          np.real([expected_final_state[1][0][0]])])
                    if np.abs(expected_final_state_real[0][0] - 1.0) <= 0.01:  # bottom of bloch sphere 'down' (I'll call it 0)
                        #print('expected ~ 1: ', expected_final_state_real[0][0])
                        zero_or_one = 0
                    elif np.abs(expected_final_state_real[0][0]) <= 0.01:
                        #print('expected ~ 0: ', expected_final_state_real[0][0])
                        zero_or_one = 1
                    else:
                        print('yo dude problem here')
                    states_file.write(str(j) + '_' + str(i + 1) + '_' + str(k + 1) + ',' + str(zero_or_one) + '\n')
                    alternating_pauli_sequence = changing_pauli_frame_sequence(final_gate_sequence)
                    experiment_sequence = gate_to_experiment_params(alternating_pauli_sequence)
                    with open(path + '/Sequence_' + str(j) + '_' + str(i + 1) + '_' + str(k + 1) + '.csv', 'w') as file:
                        for p in experiment_sequence:
                            if p[0] == False:
                                file.write(str(p[1]) + ',' + str(p[2]) + ',0\n')
                            else:
                                file.write(str(p[1]) + ',' + str(p[2]) + ',1\n')
                    file.close()
    states_file.close()
