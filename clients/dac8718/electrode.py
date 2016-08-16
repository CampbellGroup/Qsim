

class Electrode(object):

    def __init__(self, name):
        self.name = name
        self._set_number()
        # Nominally the self.currentvalues value below.

        # DAC bit value.
        self._bit_value = None

    def _set_number(self):
        """
        Assumes self.name = 'DAC X' where X is a single digit number.
        """
        number = int(self.name[-1])
        self.number = number

    def _get_voltage_from_bit_value(self):
        voltage = 2.2888e-4*self._bit_value - 7.5
        return voltage

    def _get_bit_value_from_voltage(self):
        bit_value = (self._voltage + 7.4)/2.2888e-4
        return int(bit_value)

    @property
    def voltage(self):
        return self._voltage

    @voltage.setter
    def voltage(self, value):
        self._voltage = value
        self._bit_value = self._get_bit_value_from_voltage()

    @property
    def bit_value(self):
        return self._bit_value

    @bit_value.setter
    def bit_value(self, value):
        self._bit_value = value
        new_voltage = self._get_voltage_from_bit_value()
        self._voltage = new_voltage
