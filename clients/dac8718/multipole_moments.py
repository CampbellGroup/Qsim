
class MultipoleMoments(object):
    """
    Electric potential multipole moments to second order.

    The DAC will change these values independently, giving orthogonal control
    over the DC electric field.  Follows the German diploma thesis naming
    convention.
    """

    def __init__(self):
        # Monpole moment
        self.M_0 = None
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
