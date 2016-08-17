import unittest as ut
from Qsim.clients.dac8718.electrodes import Electrodes


class TestScattering(ut.TestCase):
    """
    """
    def setUp(self):
        # bit values from 2016-08-16
        initial_bit_values = {}
        initial_bit_values['DAC 0'] = 28442
        initial_bit_values['DAC 1'] = 33622
        initial_bit_values['DAC 2'] = 36444
        initial_bit_values['DAC 3'] = 31324
        initial_bit_values['DAC 4'] = 29507
        initial_bit_values['DAC 5'] = 34696
        initial_bit_values['DAC 6'] = 36507
        initial_bit_values['DAC 7'] = 31398
        self.electrodes = Electrodes()
        for key in initial_bit_values.keys():
            bit_value = initial_bit_values[key]
            self.electrodes.set_electrode_bit_value(name=key,
                                                    value=bit_value)

        self.electrodes.initialize_multipole_values()

    def tearDown(self):
        self.electrodes = None
        del self.electrodes

    def test_dac_0_voltage(self):
        expected_voltage = -0.99019504
        voltage = self.electrodes.get_electrode_voltage(name='DAC 0')
        self.assertAlmostEqual(expected_voltage, voltage, 5)

    def test_update_voltages_from_multipole_moments(self):
        self.electrodes.update_voltages_from_multipole_moments()

    def test_get_multipole_vector_without_monopole(self):
        mm = self.electrodes.multipole_moments
        mm.get_multipole_vector_without_monopole()

