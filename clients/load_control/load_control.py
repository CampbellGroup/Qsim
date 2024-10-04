import logging

from PyQt5.QtWidgets import *
from twisted.internet.defer import inlineCallbacks

from common.lib.clients.connection import Connection
from common.lib.clients.qtui.QCustomSpinBox import QCustomSpinBox
from common.lib.clients.qtui.switch import QCustomSwitchChannel
from common.lib.clients.qtui.timer import QCustomTimer

logger = logging.getLogger(__name__)

try:
    TRAP_SOUND = "/home/qsimexpcontrol/Music/trap.wav"
    FAIL_SOUND = "/home/qsimexpcontrol/Music/swvader01.wav"
    from playsound import playsound

    SOUND_LOADED = True
except (ImportError, FileNotFoundError):
    logger.error("Sounds not loaded")
    SOUND_LOADED = False

SIGNALID = 112983


class LoadControl(QFrame):

    def __init__(self, reactor, cxn=None):
        # noinspection PyArgumentList

        super(LoadControl, self).__init__()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        self.setFrameStyle(QFrame.StyledPanel | QFrame.Plain)
        self.reactor = reactor
        self.changing = False
        self.cxn = cxn
        self.connect()

    @inlineCallbacks
    def connect(self):
        """
        Creates an Asynchronous connection to arduinottl and
        connects incoming signals to relevant functions
        """
        from labrad.units import WithUnit as U

        self.U = U
        if self.cxn is None:
            self.cxn = yield Connection(name="Load Control")
            yield self.cxn.connect()
        self.pmt = yield self.cxn.get_server("normalpmtflow")
        self.pv = yield self.cxn.get_server("parametervault")
        # self.arduinottl = yield self.cxn.get_server("arduinottl")
        self.oven = yield self.cxn.get_server("ovenserver")
        self.reg = yield self.cxn.get_server("registry")
        try:
            yield self.reg.cd(["", "settings"])
            self.settings = yield self.reg.dir()
            self.settings = self.settings[1]
        except ImportError:
            self.settings = []
        yield self.setup_listeners()
        yield self.initialize_gui()

    @inlineCallbacks
    def setup_listeners(self):
        yield self.pmt.signal__new_count(SIGNALID)
        yield self.pmt.addListener(
            listener=self.on_new_counts, source=None, ID=SIGNALID
        )

    # noinspection PyArgumentList
    @inlineCallbacks
    def initialize_gui(self):
        layout = QGridLayout()
        self.master_button = QCustomSwitchChannel(
            "Master Load Switch", ("Open/Oven On", "Closed/Oven Off")
        )
        self.master_button.setFrameStyle(QFrame.NoFrame)
        self.master_button.TTLswitch.toggled.connect(self.master_toggle)

        self.button_399 = QCustomSwitchChannel("399 Shutter", ("Open", "Closed"))
        self.button_399.setFrameStyle(QFrame.NoFrame)
        self.button_399.TTLswitch.toggled.connect(self.set_shutter_state_399)

        self.button_protection = QCustomSwitchChannel("Protection Beam Shutter", ("Open", "Closed"))
        self.button_protection.setFrameStyle(QFrame.NoFrame)
        self.button_protection.TTLswitch.toggled.connect(self.set_shutter_state_protection)


        self.timer_widget = QCustomTimer("Loading Time", show_control=False)
        self.current_widget = QCustomSpinBox((0.0, 5.0), title="Oven current", suffix="A")
        self.max_time_widget = QCustomSpinBox((0.0, 30.0), title="Max time", suffix="m")

        self.current_widget.set_step_size(0.01)
        self.current_widget.set_decimals(2)
        self.current_widget.spin_level.valueChanged.connect(self.current_changed)

        self.max_time_widget.set_value(10.0)
        self.max_time_widget.set_step_size(0.1)
        self.max_time_widget.set_decimals(1)

        if "oven" in self.settings:
            value = yield self.reg.get("oven")
            self.current_widget.spin_level.setValue(value)
        self.master_button.TTLswitch.setChecked(False)

        if "399 trapshutter" in self.settings:
            value = yield self.reg.get("399 trapshutter")
            value = bool(value)
            self.button_399.TTLswitch.setChecked(value)
        else:
            self.button_399.TTLswitch.setChecked(False)

        if "protection trapshutter" in self.settings:
            value = yield self.reg.get("protection trapshutter")
            value = bool(value)
            self.button_protection.TTLswitch.setChecked(value)
        else:
            self.button_protection.TTLswitch.setChecked(False)

        layout.addWidget(self.master_button, 0, 0, 1, 2)
        layout.addWidget(self.button_399, 1, 0, 1, 2)
        layout.addWidget(self.button_protection, 2, 0, 1, 2)
        layout.addWidget(self.current_widget, 3, 0, 1, 1)
        layout.addWidget(self.max_time_widget, 3, 1, 1, 1)
        layout.addWidget(self.timer_widget, 4, 0, 1, 2)
        self.setLayout(layout)

    @inlineCallbacks
    def on_new_counts(self, signal, pmt_value):
        # this throws error on closeout since listner is yielding to server
        disc_value = yield self.pv.get_parameter("Loading", "ion_threshold")
        switch_on = self.master_button.TTLswitch.isChecked()
        if (pmt_value >= disc_value) and switch_on:
            self.master_button.TTLswitch.setChecked(False)
            if SOUND_LOADED:
                playsound(TRAP_SOUND)
        elif (
                self.timer_widget.time
                >= float(self.max_time_widget.spin_level.value()) * 60.0
        ) and switch_on and not self.changing:
            self.master_button.TTLswitch.setChecked(False)
            if SOUND_LOADED:
                playsound(FAIL_SOUND)

    @inlineCallbacks
    def master_toggle(self, value):
        self.changing = True
        if value:
            self.timer_widget.reset()
            self.timer_widget.start()
            yield self.oven.oven_output(True)
            yield self.button_399.TTLswitch.setChecked(True)
            yield self.button_protection.TTLswitch.setChecked(True)
        else:
            yield self.oven.oven_output(False)
            yield self.button_399.TTLswitch.setChecked(False)
            #            yield self.button_protection.TTLswitch.setChecked(False)
            self.timer_widget.reset()
        self.changing = False

    @inlineCallbacks
    def current_changed(self, value: float):
        """:param value: The current in amps"""
        yield self.oven.oven_current(self.U(value, "A"))
        if "oven" in self.settings:
            yield self.reg.set("oven", value)

    @inlineCallbacks
    def set_shutter_state_399(self, state: bool) -> None:
        """:param state: a bool representing whether the state is toggled on or off"""
        if "399 trapshutter" in self.settings:
            yield self.reg.set("399 trapshutter", state)
        p = yield self.oven.shutter_output_399(state)

    @inlineCallbacks
    def set_shutter_state_protection(self, state: bool) -> None:
        """:param state: a bool representing whether the state is toggled on or off"""
        if "protection trapshutter" in self.settings:
            yield self.reg.set("protection trapshutter", state)
        p = yield self.oven.shutter_output_protection(state)

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QApplication([])
    import qt5reactor

    qt5reactor.install()
    from twisted.internet import reactor

    LoadControlWidget = LoadControl(reactor)
    LoadControlWidget.show()
    # noinspection PyUnresolvedReferences
    reactor.run()
