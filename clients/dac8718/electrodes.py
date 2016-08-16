import numpy as np
import collections as _collections
from electrode import Electrode
from multipole_moments import MultipoleMoments


class Electrodes(object):
    def __init__(self):
        # Access electrodes by name.
        self._electrode_dict = _collections.OrderedDict()
        self._populate_electrodes_dict()

        # Repetition of electrode collections
        self._set_electrode_collections()
        self.multipole_moments = MultipoleMoments()
        self._set_multipole_transfer_matrices()

    def _populate_electrodes_dict(self):
        # TODO: better way to populate this dictionary.
        for channel_number in xrange(8):
            dac_name = 'DAC %s' % channel_number
            electrode = Electrode(name=dac_name)
            self._electrode_dict[electrode.name] = electrode

    def _set_electrode_collections(self):
        """
        Set list collections of the different electrode names for accessing
        various multipole moments of the electrodes.
        """
        self._top = ['DAC 0', 'DAC 1', 'DAC 2', 'DAC 3']
        self._bottom = ['DAC 4',  'DAC 5', 'DAC 6', 'DAC 7']
        self._x_minus = ['DAC 2', 'DAC 6']
        self._x_plus = ['DAC 0', 'DAC 4']
        self._y_minus = ['DAC 1', 'DAC 5']
        self._y_plus = ['DAC 3', 'DAC 7']

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

    def get_electrode_value(self, name=None):
        """
        Returns electrode bit value (float?) given the electrode name (str).
        """
        electrode = self._electrode_dict[name]
        return electrode.value

    def get_electrode_voltage(self, name=None):
        """
        Returns float for electrode voltage value given the electrode name.
        """
        electrode = self._electrode_dict[name]
        return electrode.voltage

    def set_electrode_value(self, name=None, value=None):
        """
        Set electrode bit value (float?) given the electrode name (str).
        """
        self._electrode_dict[name].value = value

    def get_electrode_number(self, name=None):
        """
        Returns int for electrode number.
        """
        electrode = self._electrode_dict[name]
        return electrode.number

    def update_voltages_from_multipole_moments(self):
        """
        Matrix transformation from multipole moments to electrode voltages.
        """
        vector = self.multipole_moments.get_multipole_vector_without_monopole()
        voltages = self.multipole_to_electrode_matrix * vector
        for kk in xrange(len(voltages)):
            voltage = voltages[kk]
            # Updates the ordered dict values by position.
            self._electrode_dict[self._electrode_dict.keys()[kk]] = voltage

    @property
    def z_electrodes(self):
        """
        List of all electrode names.
        """
        electrode_names = self._top + self._bottom
        return electrode_names
