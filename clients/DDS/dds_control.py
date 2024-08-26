from twisted.internet.defer import inlineCallbacks
from PyQt5.QtWidgets import *
from common.lib.clients.Pulser2_DDS.dds_control import DDSControlWidget

import logging

logger = logging.getLogger(__name__)


class ScriptResponsiveDDSControlWidget(DDSControlWidget):

    @inlineCallbacks
    def initialize(self):
        super().initialize()

        # Extra functionality so that the widget is disables while the script scanner is running a script

        sc = yield self.cxn.get_server("ScriptScanner")

        yield sc.signal_on_running_new_script(self.SIGNALID + 1, context=self.context)
        yield sc.signal_on_running_script_finished(
            self.SIGNALID + 2, context=self.context
        )

        yield sc.addListener(
            listener=self.disable,
            source=None,
            ID=self.SIGNALID + 1,
            context=self.context,
        )
        yield sc.addListener(
            listener=self.enable,
            source=None,
            ID=self.SIGNALID + 2,
            context=self.context,
        )


if __name__ == "__main__":
    a = QApplication([])
    import qt5reactor

    qt5reactor.install()
    from twisted.internet import reactor

    trap_drive_Widget = ScriptResponsiveDDSControlWidget(reactor)
    trap_drive_Widget.show()
    reactor.run()
