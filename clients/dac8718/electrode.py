

class Electrode(object):

    def __init__(self, name):
        self.name = name
        self._set_number()
        # Nominally the self.currentvalues value below.

        # DAC bit value.
        self.value = None

    def _set_number(self):
        """
        Assumes self.name = 'DAC X' where X is a single digit number.
        """
        number = int(self.name[-1])
        self.number = number

    def get_voltage(self):
        bit = self.value
        voltage = (2.2888e-4*bit - 7.5)
        return voltage

    @property
    def voltage(self):
        return self.get_voltage()
