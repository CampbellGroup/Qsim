import collections as _collections
import numpy as np


class MultipoleMoments(object):
    """
    Electric potential multipole moments to second order.

    The DAC will change these values independently, giving orthogonal control
    over the DC electric field.  Follows the German diploma thesis naming
    convention.  We are dropping the monopole moment.
    """

    def __init__(self):
        # Dipole moments
        self.M_1 = None
        self.M_2 = None
        self.M_3 = None
        # Quadrupole moments
        self.M_4 = None
        self.M_5 = None
        self.M_6 = None
        self.M_7 = None
        self.M_8 = None
        self._multipole_dict = _collections.OrderedDict()
        self._set_multipole_dict()

    def _set_multipole_dict(self):
        """
        Useful for getting and setting values by name.
        """
        self._multipole_dict['M_1'] = self.M_1
        self._multipole_dict['M_2'] = self.M_2
        self._multipole_dict['M_3'] = self.M_3
        self._multipole_dict['M_4'] = self.M_4
        self._multipole_dict['M_5'] = self.M_5
        self._multipole_dict['M_6'] = self.M_6
        self._multipole_dict['M_7'] = self.M_7
        self._multipole_dict['M_8'] = self.M_8

    def get_value(self, name=None):
        """
        Get multipole value by name.

        Parameters
        ----------
        name: str
        """
        return self._multipole_dict[name]

    def set_value(self, name=None, value=None):
        """
        Parameters
        ----------
        name: str, name of the multiple moment, 'M_1', for example.
        value: float, voltage value to set multiple moment to.
        """
        self._multipole_dict[name] = value

    def get_multipole_vector_without_monopole(self):
        """
        Returns a numpy array of ordered multipoles starting with M_1.
        """
        multipole_moments = []
        for key, value in self._multipole_dict.items():
            multipole_moments.append(value)

        return np.array(multipole_moments)

    def set_multipole_values_from_vector(self, multipole_vector):
        """
        multipole_vector: ordered list, starting with M_1, M_2, etc.

        Exlcudes the monopole term.
        """
        self.M_1 = multipole_vector[0]
        self.M_2 = multipole_vector[1]
        self.M_3 = multipole_vector[2]
        self.M_4 = multipole_vector[3]
        self.M_5 = multipole_vector[4]
        self.M_6 = multipole_vector[5]
        self.M_7 = multipole_vector[6]
        self.M_8 = multipole_vector[7]
        self._set_multipole_dict()
