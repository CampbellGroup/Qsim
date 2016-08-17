import unittest as ut
from Qsim.clients.dac8718.electrodes import Electrodes
from Qsim.clients.dac8718.electrode import Electrode


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

    def test_update_voltages_from_multipole_moments_channel_name(self):
        self.electrodes.update_voltages_from_multipole_moments()
        expected_name = 'DAC 0'
        electrode_list = self.electrodes.get_electrode_list()
        electrode = electrode_list[0]
        name = electrode.name
        self.assertEqual(expected_name, name)

    def test_get_multipole_vector_without_monopole(self):
        mm = self.electrodes.multipole_moments
        mm.get_multipole_vector_without_monopole()

    def test_electrode_name(self):
        expected_name = 'DAC 0'
        electrode = self.electrodes.get_electrode(name='DAC 0')
        name = electrode.name
        self.assertEqual(expected_name, name)

    def test_electrode_list_electrode_name(self):
        expected_name = 'DAC 0'
        electrode_list = self.electrodes.get_electrode_list()
        electrode = electrode_list[0]
        name = electrode.name
        self.assertEqual(expected_name, name)

    def test_electrode_dict_access(self):
        """
        Get an electrode by position and test its type.
        """
        electrode = self.electrodes._electrode_dict.items()[0][1]
        self.assertIsInstance(obj=electrode, cls=Electrode)
