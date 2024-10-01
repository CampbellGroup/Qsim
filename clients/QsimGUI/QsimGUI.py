#!/usr/bin/python
import logging
import os
import sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from twisted.internet.defer import inlineCallbacks

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(levelname)s:%(module)s:%(asctime)s [-] %(message)s"
)

sys.path.append("/home/qsimexpcontrol/LabRAD/")
sys.path.append("/home/qsimexpcontrol/LabRAD/Qsim")
os.environ["LABRADPASSWORD"] = "lab"


# noinspection PyArgumentList
class QsimGUI(QMainWindow):
    def __init__(self, reactor, clipboard, parent=None):
        super(QsimGUI, self).__init__(parent)
        self.clipboard = clipboard
        self.reactor = reactor
        self.connect_labrad()

    @inlineCallbacks
    def connect_labrad(self):
        from common.lib.clients.connection import Connection

        cxn = Connection(name="Qsim GUI Client")
        yield cxn.connect()
        self.create_layout(cxn)

    # Highest level adds tabs to big GUI
    def create_layout(self, cxn):
        #  creates central layout
        central_widget = QWidget()
        layout = QHBoxLayout()

        #  create subwidgets to be added to tabs
        script_scanner = self.make_script_scanner_widget(reactor, cxn)
        wavemeter = self.make_wavemeter_widget(reactor, cxn)
        control = self.make_control_widget(reactor, cxn)
        # ev_pump = self.make_ev_pump_widget(reactor, cxn)

        # add tabs
        self.tabWidget = QTabWidget()
        self.tabWidget.addTab(wavemeter, "&Wavemeter")
        self.tabWidget.addTab(script_scanner, "&Script Scanner")
        self.tabWidget.addTab(control, "&Control")
        # self.tabWidget.addTab(ev_pump, "&EV Pump")
        # self.tabWidget.addTab(WF, '&Windfreak')

        self.tabWidget.setMovable(True)
        self.tabWidget.setCurrentIndex(2)

        layout.addWidget(self.tabWidget)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.setWindowTitle("Qsim GUI")

    ###############################################################
    # Here we will connect to individual clients and add sub-tabs #
    ###############################################################

    def make_pulser_widget(self, reactor, cxn):
        from Qsim.clients.DDS.dds_control import DDSControlWidget
        from common.lib.clients.pulser_switch.pulser_switch_control import SwitchWidget

        puls_widget = QWidget()
        grid_layout = QGridLayout()

        dds = DDSControlWidget(reactor, cxn)
        switch = SwitchWidget(reactor)
        grid_layout.addWidget(dds)
        grid_layout.addWidget(switch)
        puls_widget.setLayout(grid_layout)
        return puls_widget

    def make_piezo_widget(self, reactor, cxn):
        qwidget = QWidget()
        from common.lib.clients.piezo_client.PiezoClient import PiezoClient

        grid_layout = QGridLayout()
        pz_client = PiezoClient(reactor)
        grid_layout.addWidget(pz_client)
        qwidget.setLayout(grid_layout)
        return qwidget

    def make_ev_pump_widget(self, reactor, cxn):
        from common.lib.clients.evPump.evPumpClient import eVPumpClient

        ev_widget = QWidget()
        layout = QHBoxLayout()
        layout.addStretch()
        layout.addWidget(eVPumpClient(reactor, cxn=cxn))
        layout.addStretch()
        ev_widget.setLayout(layout)
        return ev_widget

    def make_script_scanner_widget(self, reactor, cxn):
        from common.lib.clients.script_scanner_gui.script_scanner_gui import (
            ScriptScannerGui,
        )

        scriptscanner = ScriptScannerGui(reactor, cxn=cxn)
        return scriptscanner

    def make_wavemeter_widget(self, reactor, cxn):
        # widget = QWidget()
        from common.lib.clients.Multiplexer.multiplexerclient import WavemeterClient

        # from Qsim.clients.single_wavemeter_channel.single_channel_wm import single_channel_wm
        # gridLayout = QGridLayout()
        wavemeter = WavemeterClient(reactor, cxn)
        # ws7 = single_channel_wm(reactor)
        # gridLayout.addWidget(wavemeter)
        # gridLayout.addWidget(ws7)
        # wavemeter.setMaximumHeight(800)
        # widget.setLayout(gridLayout)
        # return widget
        return wavemeter

    def make_control_widget(self, reactor, cxn):
        widget = QWidget()
        from Qsim.clients.RF_control.RFcontrol import RFControl
        from common.lib.clients.PMT_Control.pmt_control_2 import PMTWidget
        from common.lib.clients.evPump.evPumpClient import eVPumpClient


        # from Qsim.clients.cameraswitch.cameraswitch import cameraswitch
        from common.lib.clients.switchclient.switchclient import SwitchClient
        from clients.dac_control.dac_client import DACClient
        from Qsim.clients.load_control.load_control import LoadControl
        from common.lib.clients.piezo_client.PiezoClient import PiezoClient
        from common.lib.clients.keithley_2231A_30_3.keithley_2231A_30_3 import (
            KeithleyClient,
        )
        from common.lib.clients.Multiplexer.multiplexerclient import MiniWavemeterClient

        from Qsim.clients.DDS.dds_control import ScriptResponsiveDDSControlWidget
        from common.lib.clients.pulser_switch.pulser_switch_control import SwitchWidget

        # from Qsim.clients.windfreak_client.windfreak_client import WindfreakClient

        layout = QHBoxLayout()

        # addWidget(widget, vertical-pos, horizontal-pos, vertical-span, horizontal-span)
        # column one
        col_one_widget = QWidget()
        col_one = QVBoxLayout()
        col_one.addWidget(SwitchClient(reactor, cxn))
        # col_one.addWidget(cameraswitch(reactor, cxn))
        col_one.addWidget(PMTWidget(reactor, cxn))
        col_one.addWidget(LoadControl(reactor))
        col_one.addWidget(eVPumpClient(reactor, cxn))
        col_one.addStretch(1)
        col_one.addWidget(RFControl(reactor, cxn))
        col_one_widget.setLayout(col_one)
        col_one_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        layout.addWidget(col_one_widget)

        # grid_layout.addWidget(WindfreakClient(reactor), 6, 0, 1, 3)

        # column two
        col_two_widget = QWidget()
        col_two = QVBoxLayout()

        col_two.addWidget(DACClient(reactor, cxn))
        # grid_layout.addWidget(LoadControl(reactor), 4, 1, 2, 1)
        col_two.addWidget(PiezoClient(reactor))
        col_two.addWidget(KeithleyClient(reactor, cxn))
        col_two.addStretch(1)

        col_two_widget.setLayout(col_two)
        layout.addWidget(col_two_widget)
        # column three

        col_three_widget = QWidget()
        col_three = QVBoxLayout()
        col_three.addWidget(ScriptResponsiveDDSControlWidget(reactor, cxn))
        col_three.addWidget(SwitchWidget(reactor))
        col_three.addWidget(MiniWavemeterClient(reactor))
        col_three.addStretch(1)
        col_three_widget.setLayout(col_three)
        layout.addWidget(col_three_widget)

        # grid_layout.setSpacing(1)
        widget.setLayout(layout)
        return widget

    # def make_windfreak_widget(self, reactor, cxn):
    #     from Qsim.clients.windfreak_client.windfreak_client import WindfreakClient
    #     wf_client = WindfreakClient(reactor)
    #     return wf_client

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QApplication(sys.argv)
    clipboard = a.clipboard()
    import qt5reactor

    qt5reactor.install()
    from twisted.internet import reactor

    gui = QsimGUI(reactor, clipboard)
    gui.setWindowIcon(QtGui.QIcon("/home/qsimexpcontrol/Pictures/icons/6ions.jpg"))
    gui.setWindowTitle("Qsim GUI")
    gui.show()
    reactor.run()
