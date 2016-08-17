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
        self._multipole_dict = _collections.OrderedDict()
        self._set_multipole_dict()

    def _set_multipole_dict(self):
        """
        Useful for getting and setting values by name.
        """
        # Dipole moments
        self._multipole_dict['M_1'] = 0
        self._multipole_dict['M_2'] = 0
        self._multipole_dict['M_3'] = 0
        # Quadrupole moments
        self._multipole_dict['M_4'] = 0
        self._multipole_dict['M_5'] = 0
        self._multipole_dict['M_6'] = 0
        self._multipole_dict['M_7'] = 0
        self._multipole_dict['M_8'] = 0

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
        self.set_value(name='M_1', value=multipole_vector[0])
        self.set_value(name='M_2', value=multipole_vector[1])
        self.set_value(name='M_3', value=multipole_vector[2])
        self.set_value(name='M_4', value=multipole_vector[3])
        self.set_value(name='M_5', value=multipole_vector[4])
        self.set_value(name='M_6', value=multipole_vector[5])
        self.set_value(name='M_7', value=multipole_vector[6])
        self.set_value(name='M_8', value=multipole_vector[7])
