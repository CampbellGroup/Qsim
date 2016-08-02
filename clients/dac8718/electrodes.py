import numpy as np
from electrode import Electrode


class Electrodes(object):
    def __init__(self):
        # Access electrodes by name.
        self._electrode_dict = {}
        self._populate_electrodes_dict()

        # Repetition of electrode collections
        self._set_electrode_collections()

    def _populate_electrodes_dict(self):
        # TODO: better way to populate this dictionary.
        electrode_0 = Electrode(name='DAC 0')
        self._electrode_dict[electrode_0.name] = electrode_0
        electrode_1 = Electrode(name='DAC 1')
        self._electrode_dict[electrode_1.name] = electrode_1
        electrode_2 = Electrode(name='DAC 2')
        self._electrode_dict[electrode_2.name] = electrode_2
        electrode_3 = Electrode(name='DAC 3')
        self._electrode_dict[electrode_3.name] = electrode_3
        electrode_4 = Electrode(name='DAC 4')
        self._electrode_dict[electrode_4.name] = electrode_4
        electrode_5 = Electrode(name='DAC 5')
        self._electrode_dict[electrode_5.name] = electrode_5
        electrode_6 = Electrode(name='DAC 6')
        self._electrode_dict[electrode_6.name] = electrode_6
        electrode_7 = Electrode(name='DAC 7')
        self._electrode_dict[electrode_7.name] = electrode_7

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

    @property
    def z_electrodes(self):
        """
        List of all electrode names.
        """
        electrode_names = self._top + self._bottom
        return electrode_names

    @property
    def x_dipole_moment(self):
        return self._dipole_moment(self._x_plus, self._x_minus)

    @property
    def y_dipole_moment(self):
        return self._dipole_moment(self._y_plus, self._y_minus)

    @property
    def z_dipole_moment(self):
        # TODO: consider name changes for the z-electrode values
        return self._dipole_moment(self._top, self._bottom)

    def _dipole_moment(self, plus_electrodes, minus_electrodes):
        """
        Return the dipole moment between the plus and minus electrodes.

        Parameters
        ----------
        plus_electrodes: list of strs, plus electrode names.
        minus_electrodes: list of strs, minus electrode names.
        """
        plus_values = [self.get_electrode_voltage(name) for name in
                       plus_electrodes]

        minus_values = [self.get_electrode_voltage(name) for name in
                        minus_electrodes]

        plus_mean = np.mean(plus_values)
        minus_mean = np.mean(minus_values)
        dipole_moment = plus_mean - minus_mean
        return dipole_moment

    @property
    def x_squeeze_moment(self):
        electrodes = self._x_plus + self._x_minus
        return self._squeeze_moment(electrodes)

    @property
    def y_squeeze_moment(self):
        electrodes = self._y_plus + self._y_minus
        return self._squeeze_moment(electrodes)

    @property
    def z_squeeze_moment(self):
        electrodes = self._top + self._bottom
        return self._squeeze_moment(electrodes)

    def _squeeze_moment(self, electrodes):
        values = [self.get_electrode_voltage(name) for name in electrodes]
        squeeze_moment = np.mean(values)
        return squeeze_moment
