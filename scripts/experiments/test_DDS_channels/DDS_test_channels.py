import labrad
from labrad.units import WithUnit
from common.lib.servers.abstractservers.script_scanner.scan_methods import experiment
from twisted.internet.defer import inlineCallbacks
import time
class DDS_test_channels(experiment):
    
    name = 'DDS Channel Tester'

    exp_parameters = []
    exp_parameters.append(('testDDS', 'duration'))
    exp_parameters.append(('testDDS', 'frequency'))
    exp_parameters.append(('testDDS', 'power'))
    exp_parameters.append(('testDDS', 'phase'))
    exp_parameters.append(('testDDS', 'ramprate'))
    exp_parameters.append(('testDDS', 'ampramprate'))
    exp_parameters.append(('testDDS', 'cycles'))


    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters
    
    def initialize(self, cxn, context, ident):
	from labrad.units import WithUnit as U
	self.U = U
        self.ident = ident
        self.cxn = labrad.connect(name = 'DDS Channel Tester')
	self.pulser = cxn.pulser
	self.chans = self.pulser.get_dds_channels()
	self.starttime = self.U(0.001,'s')
	self.p = self.parameters
        
    def run(self, cxn, context):
	
	self.pulser.new_sequence()		
        for i, channame in enumerate(self.chans):

		self.pulser.add_dds_pulses([(channame, self.starttime, self.p.testDDS.duration, self.p.testDDS.frequency, self.U(-48.0,'dBm'), self.p.testDDS.phase, self.p.testDDS.ramprate, self.p.testDDS.ampramprate)])		

		self.pulser.add_dds_pulses([(channame, self.starttime + self.p.testDDS.duration, self.p.testDDS.duration/2, self.p.testDDS.frequency, self.p.testDDS.power, self.p.testDDS.phase, self.p.testDDS.ramprate, self.p.testDDS.ampramprate)])

		self.pulser.add_dds_pulses([(channame, self.starttime + 2*self.p.testDDS.duration, self.p.testDDS.duration/2, self.p.testDDS.frequency, self.p.testDDS.power, self.p.testDDS.phase + self.U(45*i,'deg'), self.p.testDDS.ramprate, self.p.testDDS.ampramprate)])

		self.pulser.add_dds_pulses([(channame, self.starttime + 5/2*self.p.testDDS.duration, self.p.testDDS.duration, self.p.testDDS.frequency, self.U(-48.0,'dBm'), self.p.testDDS.phase, self.p.testDDS.ramprate, self.p.testDDS.ampramprate)])
	self.pulser.program_sequence()
	self.pulser.start_number(int(self.p.testDDS.cycles))
	

    def finalize(self, cxn, context):
	self.pulser.stop_sequence()
        self.cxn.disconnect()

            

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = DDS_test_channels(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)




