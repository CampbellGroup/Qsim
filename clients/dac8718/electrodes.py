import numpy as np
import collections as _collections
from electrode import Electrode
from multipole_moments import MultipoleMoments


class Electrodes(object):
    def __init__(self):
        # Access electrodes by name.
        self._electrode_dict = _collections.OrderedDict()
        self._populate_electrodes_dict()

        self.multipole_moments = MultipoleMoments()
        self._set_multipole_transfer_matrices()

    def initialize_multipole_values(self):
        """
        Set the multipole vector based on the electrode voltages.
        """
        voltage_vector = self._get_electrode_voltage_vector()
        mp_vector = self.electrode_to_multipole_matrix.dot(voltage_vector)
        self.multipole_moments.set_multipole_values_from_vector(mp_vector)

    def _get_electrode_voltage_vector(self):
        """
        Returns a numpy array for matrix multiplication.
        """
        voltage_vector = []
        for electrode in self._electrode_dict.values():
            voltage = electrode.voltage
            voltage_vector.append(voltage)
        return np.array(voltage_vector)

    def get_electrode(self, name=None):
        """
        Returns an electrode instance from the dict.
        """
        return self._electrode_dict[name]

    def get_electrode_bit_value(self, name=None):
        """
        Returns electrode bit value given the electrode name (str).
        """
        electrode = self._electrode_dict[name]
        return electrode.bit_value

    def get_electrode_voltage(self, name=None):
        """
        Returns float for electrode voltage value given the electrode name.
        """
        electrode = self._electrode_dict[name]
        return electrode.voltage

    def set_electrode_bit_value(self, name=None, value=None):
        """
        Set electrode bit value given the electrode name (str).
        """
        self._electrode_dict[name].bit_value = value

    def get_electrode_number(self, name=None):
        """
        Returns int for electrode number.
        """
        electrode = self._electrode_dict[name]
        return electrode.number

    def get_electrode_list(self):
        return self._electrode_dict.values()

    def update_voltages_from_multipole_moments(self):
        """
        Matrix transformation from multipole moments to electrode voltages.
        """
        vector = self.multipole_moments.get_multipole_vector_without_monopole()
        voltages = self.multipole_to_electrode_matrix.dot(vector)
        for kk in xrange(len(voltages)):
            voltage = voltages[kk]
            # Updates the ordered dict values by position.
            self._electrode_dict.items()[kk][1].voltage = voltage

    def _populate_electrodes_dict(self):
        for channel_number in xrange(8):
            dac_name = 'DAC %s' % channel_number
            electrode = Electrode(name=dac_name)
            self._electrode_dict[electrode.name] = electrode

    def _set_multipole_transfer_matrices(self):
        """
        Matrices derived from fitting comsol simulations of the trap geometry.
        """
        row_1 = [-7.98491456e+04, 9.97290504e+03, -8.34753779e+02,
                 7.83711367e+05, 1.60632984e+06, 2.07110112e+09,
                 -9.21613019e+05, -6.47489511e+06]

        row_2 = [9.08217330e+04, -1.26262665e+04, 1.72276248e+03,
                 -8.77337835e+05, -1.19566908e+06, -2.31777025e+09,
                 8.72739472e+05, 7.40424900e+06]

        row_3 = [-8.33511849e+04, 1.00807327e+04, -8.42031614e+02,
                 7.83322761e+05, 1.61682392e+06, 2.09390837e+09,
                 -9.31852246e+05, -6.83102436e+06]

        row_4 = [7.74809889e+04, -8.14548331e+03, 1.46261072e+03,
                 -7.39129168e+05, -1.03420689e+06, -1.97729719e+09,
                 1.02982636e+06, 6.31653529e+06]

        row_5 = [7.83056368e+04, -9.35883102e+03, 7.44032820e+02,
                 -3.96139461e+03, -1.02615220e+06, -1.96518036e+09,
                 8.83825337e+05, 6.13498121e+06]

        row_6 = [-7.50714648e+04, 7.79852359e+03, -1.41418832e+03,
                 -1.51076112e+04, 1.52982245e+06, 1.91561317e+09,
                 -7.22981923e+05, -6.11870080e+06]

        row_7 = [7.54130105e+04, -9.32179831e+03, 7.41447591e+02,
                 -3.88766024e+03, -1.02233674e+06, -1.95737952e+09,
                 8.80325442e+05, 6.39450469e+06]

        row_8 = [-8.01616368e+04, 1.10981675e+04, -1.51302236e+03,
                 3.74643059e+04, 1.59176500e+06, 2.04552764e+09,
                 -1.05562593e+06, -6.53377462e+06]

        matrix = np.array([row_1, row_2, row_3, row_4, row_5, row_6, row_7,
                           row_8])

        self.multipole_to_electrode_matrix = matrix

        self._set_electrode_to_multipole_matrix()

    def _set_electrode_to_multipole_matrix(self):
        """
        The inverse of the multipole_to_electrode_matrix
        """
        inverted_matrix = np.linalg.inv(self.multipole_to_electrode_matrix)
        self.electrode_to_multipole_matrix = inverted_matrix
