"""
The hardware control code depends on LabRAD.  Therefore LabRAD must
be running to test this code.

TODO: better implementation where LabRAD is started somehow from this code/or
overall code testing on Magic to make this more automatic.
"""




from twisted.trial.unittest import TestCase

import labrad



class Test_rigolDG1022A(TestCase):
    
    debug = True


    def setUp(self):
        """
        Connect to labrad
        """
        self.cxn = labrad.connect('10.97.112.2') #host='localhost')

    
    def tearDown(self):
        """
        Disconnect from labrad
        """
        self.cxn.disconnect()


    def _get_tester(self):
        """
        Connect to AgilentE3633AServer.  Check that the labrad connection
        has this servers attribute.
        
        Returns
        -------
        cxn.agilent_e3633a: labrad server
        """
        self.assert_(hasattr(self.cxn, 'gpib_device_manager'))
        self.assert_(hasattr(self.cxn, 'rigol_dg1022a_server'))
        return self.cxn.rigol_dg1022a_server
    

    def test_echo(self):
        """
        Test that server has basic function echo
        """
        server = self._get_tester()
        self.assert_(hasattr(server, 'echo'))


    def test_name(self):
        """
        Test server name
        """
        server = self._get_tester()
        resp = server.name
        
        expected_resp = 'Rigol DG1022A Server'
        
        self.assertEquals(resp, expected_resp)   


    def test_list_devices(self):
        """
        Hardware dependent test that checks for list devices
        
        TODO: somehow replace device with a mock device that provides this 
        information
        """        
        server = self._get_tester()
        resp = server.list_devices()
        
        expected_resp = [(0L, 'wsu2campbell GPIB Bus - USB0::0x0400::0x09C4::DG1F150100011'), 
                         (1L, 'wsu2campbell GPIB Bus - USB0::0x0400::0x09C4::DG1F141800334'), 
                         (2L, 'wsu2campbell GPIB Bus - USB0::0x0400::0x09C4::DG1F141800371')]
        
        self.assertEquals(resp, expected_resp)
        
    
    
    
    def test_apply_dc(self):
        """
        """
        
        server = self._get_tester()
        server.select_device(0)
        
        resp   = server.apply_dc(1)
        
        expected_resp = labrad.units.WithUnit(0.0, 'V')
        
        self.assertEquals(resp, expected_resp)

#
#
#if __name__ == '__main__':
#    test()
#
#