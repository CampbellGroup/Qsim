import unittest as ut
from Qsim.clients.dac8718.electrodes import Electrodes


class TestScattering(ut.TestCase):
    """
    """
    def setUp(self):
        self.electrodes = Electrodes()

    def tearDown(self):
        self.electrodes = None
        del self.electrodes
