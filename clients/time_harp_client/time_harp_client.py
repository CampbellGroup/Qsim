from twisted.internet.defer import inlineCallbacks
from common.lib.clients.connection import connection
from PyQt4 import QtGui, QtCore
import numpy as np
import time

SIGNALID1 = 421656
SIGNALID2 = 444299
SIGNALID3 = 441289


class timeharp_spinbox(QtGui.QDoubleSpinBox):
    def __init__(self, minimum, maximum, function, init_value, units=None):
        super(timeharp_spinbox, self).__init__()
        self.setFont(QtGui.QFont('MS Shell Dlg 2', pointSize=16))
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setKeyboardTracking(False)
        self.valueChanged.connect(function)
        if units is not None:
            self.setValue(init_value[units])
        else:
            self.setValue(init_value)


class TimeHarpClient(QtGui.QWidget):

    def __init__(self, reactor, cxn=None):
        super(TimeHarpClient, self).__init__()
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.cxn = cxn
        self.reactor = reactor
        from labrad.units import WithUnit as U
        self.U = U
        self.connect()

    @inlineCallbacks
    def connect(self):
        """Creates an Asynchronous connection to timeharpserver
        """
        if self.cxn is None:
            self.cxn = connection(name='Time Harp Client')
            yield self.cxn.connect()
        self.server = yield self.cxn.get_server('timeharpserver')
        self.data_vault = yield self.cxn.get_server('data_vault')
        self.grapher = yield self.cxn.get_server('grapher')
        self.pulser = yield self.cxn.get_server('pulser')
        self.reg = yield self.cxn.get_server('registry')
        yield self.reg.cd(['', 'settings'])

        yield self.server.signal__sync_rate_changed(SIGNALID1)
        yield self.server.signal__count_rate_changed(SIGNALID2)
        yield self.server.signal__warning_changed(SIGNALID3)

        yield self.server.addListener(listener=self.update_sync_count,
                                      source=None, ID=SIGNALID1)
        yield self.server.addListener(listener=self.update_count_rate, source=None,
                                      ID=SIGNALID2)
        yield self.server.addListener(listener=self.update_warnings, source=None,
                                      ID=SIGNALID3)
        self.initialize_GUI()

    @inlineCallbacks
    def initialize_GUI(self):
        layout = QtGui.QGridLayout()
        font = QtGui.QFont()
        font.setBold(True)
        font.setPointSize(18)
        self.title = QtGui.QLabel('TimeHarp 260P')
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        labels = ['Sync Channel', 'Count Channel', 'Level (mV)', 'Zero Crossing (mV)', 'Level (mV)',
                  'Zero Crossing (mV)', 'Measurement Time (ms)', 'Binning (Nx25ps)', 'Sync Divider',
                  'Sync Offset (ps)', 'Count Offset (ns)', 'Set Input Enable', 'Histogram Length',
                  'Histogram Iterations', '935']

        self.settings = ['picoharp_binning', 'picoharp_channel_level', 'picoharp_channel_zerox',
                         'picoharp_measure_time', 'picoharp_sync_level', 'picoharp_sync_zerox',
                         'picoharp_sync_divider', 'picoharp_count_offset', 'picoharp_sync_offset',
                         'picoharp_mode', 'picoharp_histo_iterations']

        init_settings = []
        for setting in self.settings:
            value = yield self.reg.get(setting)
            init_settings.append(value)

        qlabels = [QtGui.QLabel(label) for label in labels]

        font.setBold(True)
        font.setPointSize(18)
        self.title = QtGui.QLabel('TimeHarp')
        self.setSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Fixed)
        self.title.setFont(font)
        self.title.setAlignment(QtCore.Qt.AlignCenter)

        self.status = QtGui.QLabel('Status: ')
        self.status.setStyleSheet('color: blue')

        self.warning = QtGui.QLabel('Warning: ')
        self.warning.setStyleSheet('color: darkorange')
        self.warning.setMinimumHeight(200)
        self.warning.setMinimumWidth(250)

        self.errors = QtGui.QLabel('Errors: ')
        self.errors.setStyleSheet('color: red')

        self.countdisplay = QtGui.QLCDNumber()
        self.countdisplay.setDigitCount(11)
        self.countdisplay.setMinimumHeight(75)

        self.syncdisplay = QtGui.QLCDNumber()
        self.syncdisplay.setDigitCount(11)
        self.syncdisplay.setMinimumHeight(75)
        yield self.reg.cd(['', 'settings'])

        print 'creating spin boxes...'
        self.sync_level_spinbox = timeharp_spinbox(-800, 0, self.change_sync, init_settings[4], 'mV')
        self.sync_zero_spinbox = timeharp_spinbox(-40, 0, self.change_sync, init_settings[5], 'mV')
        self.count_level_spinbox = timeharp_spinbox(-800, 0.0, self.change_count, init_settings[1], 'mV')
        self.count_zero_spinbox = timeharp_spinbox(-40, 0.0, self.change_count, init_settings[2], 'mV')
        self.measure_time_spinbox = timeharp_spinbox(1.0, 10000.0, self.change_measure_time, init_settings[3], 'ms')
        self.count_offset_spinbox = timeharp_spinbox(0.0, 10000.0, self.change_count_offset, init_settings[7], 'ns')
        self.sync_offset_spinbox = timeharp_spinbox(0.0, 100000.0, self.change_sync_offset, init_settings[8], 'ps')
        self.histo_iter_spinbox = timeharp_spinbox(0.0, 50000.0, self.change_histo_iterations, init_settings[10])

        print 'creating dropdowns'
        self.binning_dropdown = QtGui.QComboBox()
        self.binning_dropdown.addItems(['1', '2', '4', '8', '16'])
        self.binning_dropdown.currentIndexChanged.connect(self.change_binning)

        self.sync_divider_dropdown = QtGui.QComboBox()
        self.sync_divider_dropdown.addItems(['1', '2', '4', '8'])
        self.sync_divider_dropdown.currentIndexChanged.connect(self.change_sync_divider)

        self.mode_dropdown = QtGui.QComboBox()
        self.mode_dropdown.addItems(['Histogramming Mode', 'T2 Mode', 'T3 Mode'])
        self.mode_dropdown.currentIndexChanged.connect(self.change_mode)

        self.repump_dropdown = QtGui.QComboBox()
        self.repump_dropdown.addItems(['On', 'Off'])

        self.histo_length_dropdown = QtGui.QComboBox()
        self.histo_length_dropdown.addItems(['25.6 ns', '51.2 ns', '102.4 ns', '204.8 ns', '409.6 ns', '819.2 ns'])
        self.histo_length_dropdown.currentIndexChanged.connect(self.change_histo_length)

        self.plot_button = QtGui.QPushButton('Plot Histogram')
        self.plot_button.clicked.connect(self.on_hist_pressed)

        self.save_timetags_button = QtGui.QPushButton('Save TimeTags')
        self.save_timetags_button.clicked.connect(self.on_timetags_pressed)

        print 'setting up widgets...'

        layout.addWidget(self.title,                 0, 0, 1, 4)
        layout.addWidget(self.mode_dropdown,         1, 0, 1, 1)
        layout.addWidget(self.status,                1, 1, 1, 1)
        layout.addWidget(self.errors,                1, 2, 1, 1)
        layout.addWidget(self.warning,               1, 3, 1, 1)
        layout.addWidget(qlabels[1],                 2, 0, 1, 2)
        layout.addWidget(qlabels[0],                 2, 2, 1, 2)
        layout.addWidget(self.countdisplay,          3, 0, 1, 2)
        layout.addWidget(self.syncdisplay,           3, 2, 1, 2)
        layout.addWidget(qlabels[2],                 4, 0, 1, 1)
        layout.addWidget(qlabels[3],                 5, 0, 1, 1)
        layout.addWidget(self.count_level_spinbox,   4, 1, 1, 1)
        layout.addWidget(self.count_zero_spinbox,    5, 1, 1, 1)
        layout.addWidget(qlabels[4],                 4, 2, 1, 1)
        layout.addWidget(qlabels[5],                 5, 2, 1, 1)
        layout.addWidget(qlabels[10],                6, 0, 1, 1)
        layout.addWidget(self.count_offset_spinbox,  6, 1, 1, 1)
        layout.addWidget(qlabels[9],                 6, 2, 1, 1)
        layout.addWidget(self.sync_offset_spinbox,   6, 3, 1, 1)
        layout.addWidget(self.sync_level_spinbox,    4, 3, 1, 1)
        layout.addWidget(self.sync_zero_spinbox,     5, 3, 1, 1)
        layout.addWidget(self.measure_time_spinbox,  9, 1, 1, 1)
        layout.addWidget(qlabels[6],                 9, 0, 1, 1)
        layout.addWidget(self.histo_iter_spinbox,   10, 1, 1, 1)
        layout.addWidget(qlabels[13],               10, 0, 1, 1)
        layout.addWidget(qlabels[14],               10, 2, 1, 1)
        layout.addWidget(self.repump_dropdown,      10, 3, 1, 1)
        layout.addWidget(self.binning_dropdown,      7, 1, 1, 1)
        layout.addWidget(self.sync_divider_dropdown, 7, 3, 1, 1,)
        layout.addWidget(qlabels[7],                 7, 0, 1, 1)
        layout.addWidget(qlabels[8],                 7, 2, 1, 1)
        layout.addWidget(qlabels[12],                9, 2, 1, 1)
        layout.addWidget(self.histo_length_dropdown, 9, 3, 1, 1)
        layout.addWidget(self.plot_button,           8, 0, 1, 4)
        layout.addWidget(self.save_timetags_button, 11, 0, 1, 4)

        self.setLayout(layout)

        init_mode = yield self.reg.get('picoharp_mode')
        init_divide = yield self.reg.get('picoharp_sync_divider')
        self.sync_divider_dropdown.setCurrentIndex(init_divide)
        self.mode_dropdown.setCurrentIndex(init_mode)
        yield self.change_mode(init_mode)
        yield self.change_sync_divider(init_divide)

    def update_sync_count(self, c, sync_count):
        self.syncdisplay.display(str(sync_count))

    def update_warnings(self, c, warning_text):
        self.warning.setText('Warning: ' + warning_text)

    @inlineCallbacks
    def update_settings(self):
        yield self.change_sync(1)
        yield self.change_count(1)
        mode = self.mode_dropdown.currentIndex()
        yield self.reg.set('picoharp_mode', mode)

    @inlineCallbacks
    def change_sync(self, value):
        level = self.sync_level_spinbox.value()
        zerox = self.sync_zero_spinbox.value()
        error = yield self.server.set_sync_discriminator(int(level), int(zerox))
        yield self.reg.set(self.settings[4], self.U(level, 'mV'))
        if error:
            self.errors.setText('Errors: ' + error[0])
        yield self.reg.set(self.settings[5], self.U(zerox, 'mV'))
        if error:
            self.errors.setText('Errors: ' + error[0])

    @inlineCallbacks
    def change_count(self, value):
        level = self.count_level_spinbox.value()
        zerox = self.count_zero_spinbox.value()
        error = yield self.server.set_input_cfd(0, int(level), int(zerox))
        if error:
            self.errors.setText('Errors: ' + error[0])
        yield self.reg.set(self.settings[1], self.U(level, 'mV'))
        yield self.reg.set(self.settings[2], self.U(zerox, 'mV'))

    @inlineCallbacks
    def on_hist_pressed(self, value):
        self.setDisabled(True)
        print 'disabled'
        init_935_power = yield self.pulser.amplitude('935SP')
        init_369DP_power = yield self.pulser.amplitude('369DP')
        yield self.pulser.amplitude('369DP', self.U(-46.0, 'dBm'))
        if self.repump_dropdown.currentIndex() == 1:
            yield self.pulser.amplitude('935SP', self.U(-46.0, 'dBm'))
        data_length_index = self.histo_length_dropdown.currentIndex()
        data_length = 2**data_length_index * (1024)
        measure_time = self.measure_time_spinbox.value()
        binning = 2**self.binning_dropdown.currentIndex()
        bins = range(32768)
        yield self.data_vault.cd(['', 'TimeHarp_histograms'], True)
        total_hist = []
        yield self.server.start_measure(int(measure_time))
        time.sleep(measure_time/1000.)
        yield self.server.stop_measure()
        data = yield self.server.get_histogram(0, 1, data_length)
        hist = np.column_stack((binning*25*np.array(bins)/1000., data))
        hist = hist.astype(float)
        total_hist.append(sum(hist[:, 1]))

#       for hist in hist_array:
        self.dataset_hist = yield self.data_vault.new('Histogram', [('run', 'arb u')],
                                                      [('Counts', 'Counts', 'num')])
        bins = []
        bins = list(np.arange(0, len(hist), 1))
        to_save = np.column_stack((bins, hist))
        print hist
        yield self.data_vault.add(hist)
        yield self.grapher.plot(self.dataset_hist, 'TimeHarp', False)
        yield self.pulser.amplitude('935SP', init_935_power)
        yield self.pulser.amplitude('369DP', init_369DP_power)
        self.setDisabled(False)

    @inlineCallbacks
    def on_timetags_pressed(self, value):
        measure_time = self.measure_time_spinbox.value()
        yield self.server.start_measure(int(measure_time))
        #time.sleep(measure_time/1000)
        data = yield self.server.read_fifo(1000)
        yield self.server.stop_measure()
        length_left = data[1]
        print length_left
        while (length_left == 1000):
            print length_left
            data += yield self.server.read_fifo(1000)
            print 'reading fifo'
        data = data[0]
        dtime_mask = 33553408
        timetags = []
        for datum in data:
            timetag = ((dtime_mask & datum) >> 10)*25./1000.
            timetags.append(timetag)

    @inlineCallbacks
    def change_binning(self, index):

        error = yield self.server.set_binning(index)
        if error:
            self.errors.setText('Errors: ' + error[0])
        yield self.reg.set(self.settings[0], index)

    @inlineCallbacks
    def change_histo_length(self, index):
        error = yield self.server.set_histo_len(index)
        if error:
            self.errors.setText('Errors: ' + error[0])

    @inlineCallbacks
    def change_count_offset(self, value):
        error = yield self.server.set_offset(int(value))
        if error:
            self.errors.setText('Errors: ' + error[0])
        yield self.reg.set(self.settings[7], self.U(value, 'ns'))

    @inlineCallbacks
    def change_sync_offset(self, value):
        error = yield self.server.set_sync_channel_offset(int(value))
        if error:
            self.errors.setText('Errors: ' + error[0])
        yield self.reg.set(self.settings[7], self.U(value, 'ps'))

    @inlineCallbacks
    def change_sync_divider(self, index):
        value = 2**int(index)
        error = yield self.server.set_sync_div(value)
        if error:
            self.errors.setText('Errors: ' + error[0])
        yield self.reg.set(self.settings[6], index)

    @inlineCallbacks
    def change_mode(self, index):
        self.status.setText('Status: Changing modes ...')
        self.setDisabled(True)
        if index == 0:
            yield self.server.initialize(index)
            yield self.update_settings()
            self.setDisabled(False)
            self.status.setText('Status: ')
            self.save_timetags_button.setDisabled(True)
            self.binning_dropdown.setDisabled(False)
            self.plot_button.setDisabled(False)
        else:
            yield self.server.initialize(index + 1)
            yield self.update_settings()
            self.setDisabled(False)
            self.status.setText('Status: ')
            self.binning_dropdown.setDisabled(True)
            self.plot_button.setDisabled(True)
            self.save_timetags_button.setDisabled(False)

    @inlineCallbacks
    def change_measure_time(self, value):
        yield self.reg.set(self.settings[3], self.U(value, 'ms'))

    @inlineCallbacks
    def change_histo_iterations(self, iterations):
        yield self.reg.set(self.settings[10], int(iterations))

    def update_count_rate(self, c, count_rate):
        self.countdisplay.display(str(count_rate))

    def closeEvent(self, x):
        self.reactor.stop()


if __name__ == "__main__":
    a = QtGui.QApplication([])
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    TimeHarpWidget = TimeHarpClient(reactor)
    TimeHarpWidget.show()
    run = reactor.run()
