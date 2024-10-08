import labrad
import numpy as np
import scipy.fftpack
from treedict import TreeDict

from Qsim.scripts.pulse_sequences.sub_sequences.record_time_tags import RecordTimeTags
from common.lib.servers.script_scanner.scan_methods import Experiment


class TD_flourescence(Experiment):

    name = "TD Flourescence"

    exp_parameters = []
    exp_parameters.append(("TrapFrequencies", "rf_drive_frequency"))
    exp_parameters.append(("TD_Flourescence", "record_time"))

    @classmethod
    def all_required_parameters(cls):
        return cls.exp_parameters

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.record_time = self.parameters.TD_Flourescence.record_time
        self.dv = cxn.data_vault
        self.pulser = cxn.pulser
        # self.grapher = cxn.grapher
        # drive_freq = self.parameters.TrapFrequencies.rf_drive_frequency
        # self.drive_period = 1/drive_freq
        # self.time_resolution = self.pulser.get_timetag_resolution()

    def programPulseSequence(self, record_time):
        seq = RecordTimeTags(
            TreeDict.fromdict({"RecordTimetags.record_timetags_duration": record_time})
        )
        seq.program_sequence(self.pulser)

    def run(self, cxn, context):
        self.programPulseSequence(self.record_time)
        self.pulser.reset_timetags()
        self.pulser.start_single()
        self.pulser.wait_sequence_done()
        self.pulser.stop_sequence()
        time_tags = self.pulser.get_timetags()
        print(len(time_tags))
        import matplotlib.pyplot as plt

        sp = scipy.fftpack.fft(time_tags)
        freq = np.linspace(0.0, 1.0 / 2.0)
        # plt.plot(time_tags, 'bo-')
        plt.plot(freq, sp.real * sp.imag)
        plt.show()
        # self.saveData(time_tags)

    def saveData(self, time_tags):
        self.dv.cd(["", "QuickMeasurements", "TD-Flourescence"], True)
        name = self.dv.new(
            "TD-Flourescence", [("time", "ns")], [("number in bin", "Arb", "Arb")]
        )
        # data = np.remainder(time_tags, self.drive_period['ns'])
        # hist, bin_edges = np.histogram(data, 200)
        x = np.array(range(len(time_tags)))
        to_plot = np.array(np.vstack((x, time_tags)).transpose(), dtype="float")
        print(time_tags)
        self.dv.add(time_tags)
        self.grapher.plot(name, "TD_Flourescence", False)
        print("Saved {}".format(name))

    def finalize(self, cxn, context):
        pass


if __name__ == "__main__":
    # normal way to launch
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = TD_flourescence(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
