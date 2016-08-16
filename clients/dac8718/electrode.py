

class Electrode(object):

    def __init__(self, name):
        self.name = name
        self._set_number()
        # Nominally the self.currentvalues value below.
        # DAC bit value.
        self.value = None

    def _set_number(self):
        # TODO: more intelligently...
        if self.name == 'DAC 0':
            self.number = 0
        elif self.name == 'DAC 1':
            self.number = 1
        elif self.name == 'DAC 2':
            self.number = 2
        elif self.name == 'DAC 3':
            self.number = 3
        elif self.name == 'DAC 4':
            self.number = 4
        elif self.name == 'DAC 5':
            self.number = 5
        elif self.name == 'DAC 6':
            self.number = 6
        elif self.name == 'DAC 7':
            self.number = 7
        else:
            self.number = None

    def get_voltage(self):
        bit = self.value
        voltage = (2.2888e-4*bit - 7.5)
        return voltage

    @property
    def voltage(self):
        return self.get_voltage()
