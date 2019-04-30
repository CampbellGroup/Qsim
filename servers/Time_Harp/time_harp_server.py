"""
### BEGIN NODE INFO
[info]
name = Time Harp Server
version = 1.0
description =
instancename = Time Harp Server

[startup]
cmdline = %PYTHON% %FILE%self.wmdll.SetPIDCourseNum
timeout = 20

[shutdown]
message = 987654321
timeout = 20
### END NODE INFO
"""

from labrad.server import LabradServer, setting
from twisted.internet.defer import returnValue
import numpy as np
from labrad.units import WithUnit as U
import ctypes


class TimeHarpServer(LabradServer):
    """
    Time harp fast time tagging server.
    """

    name = 'TimeHarpServer'

    def initServer(self):
        # load timeharp dll file
        self.U = U
        dll_path = 'C:\Windows\System32\TH260Lib.DLL'
        self.device_index = ctypes.c_int(0)
        self.thdll = ctypes.windll.LoadLibrary(dll_path)

    @setting(1, "get_errors")
    def get_errors(self, c):
        """
        Note:
        This function is provided to obtain readable error strings that explain the cause of the error better than the numerical error
        code. Use these in error handling message boxes, support enquiries etc.
        """
        func = self.thdll.TH260_GetErrorString
        func.restype = ctypes.c_int
        errstring = ctypes.create_string_buffer(40)
        errcode = ctypes.c_int()
        yield func(errstring, errcode)
        returnValue((errstring.value, errcode.value))

    @setting(2, "get_version")
    def get_version(self, c):
        """
        Note:
        Use the version information to ensure compatibility of the library with your own application.
        """
        func = self.thdll.TH260_GetLibraryVersion
        func.restype = ctypes.c_int
        vers_string = ctypes.create_string_buffer(8)
        yield func(vers_string)
        returnValue(vers_string.value)

    @setting(3, "open_device")
    def open_device(self, c):
        """
        Note:
        Opens the device for use. Must be called before any of the other functions below can be used.
        """
        func = self.thdll.TH260_OpenDevice
        func.restype = ctypes.c_int
        serial = ctypes.create_string_buffer(8)
        output = yield func(self.device_index, serial)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(4, "close_device")
    def close_device(self, c):
        """
        Note:
        Closes and releases the device for use by other programs.
        """
        func = self.thdll.TH260_CloseDevice
        func.restype = ctypes.c_int
        output = yield func(self.device_index)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(5, "initialize", mode='w')
    def initialize(self, c, mode):
        """
        measurement mode:
        0 = histogramming mode
        2 = T2 mode
        3 = T3 mode
        Note:
        This routine must be called before any of the other routines below can be used. Note that some of them depend on the meas-
        urement mode you select here. See the TimeHarp manual for more information on the measurement modes.
        """
        if mode in [0, 2, 3]:
            mode = ctypes.c_int(mode)
            func = self.thdll.TH260_Initialize
            func.restype = ctypes.c_int
            output = func(self.device_index, mode)
            if output == 0:
                returnValue('Success!')
            else:
                returnValue('Failure')

    @setting(6, "get_hardware_info")
    def get_hardware_info(self, c):
        """

        """
        func = self.thdll.TH260_GetHardwareInfo
        func.restype = ctypes.c_int
        model = ctypes.create_string_buffer(16)
        partno = ctypes.create_string_buffer(8)
        version = ctypes.create_string_buffer(16)
        output = yield func(self.device_index, model, partno, version)
        if output == 0:
            returnValue((model.value, partno.value, version.value))
        else:
            returnValue('Failure')

    @setting(7, "get_serial_number")
    def get_serial_number(self, c):
        """

        """
        func = self.thdll.TH260_GetSerialNumber
        func.restype = ctypes.c_int
        serial = ctypes.create_string_buffer(8)
        output = yield func(self.device_index, serial)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(8, "get_features")
    def get_features(self, c):
        """
        Note:
        Use the predefined bit feature values in th260defin.h (FEATURE_xxx) to extract individual bits through a bitwise AND.
        Typically this is only for information, or to check if your board has a specific (optional) capability.
        """
        func = self.thdll.TH260_GetFeatures
        func.restype = ctypes.c_int
        flags = ctypes.c_int()
        output = yield func(self.device_index, flags)
        if output == 0:
            returnValue(flags.value)
        else:
            returnValue('Failure')

    @setting(9, "get_base_resolution", returns='v[ps]')
    def get_base_resolution(self, c):
        """
        returns base resolution in ps
        Note:
        The value returned in binsteps is the maximum value allowed for the TH260_SetBinning function.
        """
        func = self.thdll.TH260_GetBaseResolution
        func.restype = ctypes.c_int
        resolution = ctypes.c_double()
        bin_steps = ctypes.c_int()
        output = yield func(self.device_index, resolution, bin_steps)
        if output == 0:
            returnValue((resolution.value, bin_steps.value))
        else:
            returnValue('Failure')

    @setting(10, "get_num_channels")
    def get_num_channels(self, c):
        """
        Note:
        The number of input channels is counting only the regular detector channels. It does not count the sync channel. Neverthe -
        less, it is possible to connect a detector also to the sync channel, e.g. in histogramming mode for antibunching or in T2
        mode.
        """
        func = self.thdll.TH260_GetNumOfInputChannels
        func.restype = ctypes.c_int
        n_channels = ctypes.c_int()
        output = yield func(self.device_index, n_channels)
        if output == 0:
            returnValue(n_channels.value)
        else:
            returnValue('Failure')

    @setting(11, "set_timing_mode", mode='w')
    def set_timing_mode(self, c, mode):
        """
        mode: 0 = Hires (25ps), 1 = Lowres (2.5 ns, a.k.a. “Long range”)
        will change the base resolution of the board
        """
        func = self.thdll.TH260_SetTimingMode
        func.restype = ctypes.c_int
        mode = ctypes.c_int(mode)
        output = yield func(self.device_index, mode)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(12, "set_sync_div", division='w')
    def set_sync_div(self, c, division):
        """
        Note: The sync divider must be used to keep the effective sync rate at values < 40 MHz.
        It should only be used with sync sources of stable period. The readings obtained with TH260_GetCountRate
        are corrected for the divider setting and deliver the external (undivided) rate. When the sync input is used
        for a detector signal the divider should be set to 1
        division: (1, 2, 4, .., SYNCDIVMAX)
        """
        func = self.thdll.TH260_SetSyncDiv
        func.restype = ctypes.c_int
        div = ctypes.c_int(division)
        output = yield func(self.device_index, div)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(13, "set_sync_discriminator", level='w[mV]', zero_crossing='w[mV]')
    def set_sync_discriminator(self, c, level, zero_crossing):
        """
        level:  CFD discriminator level in millivolts
                minimum = CFDLVLMIN
                maximum = CFDLVLMAX
        zerox: CFD zero cross level in millivolts
                minimum = CFDZCMIN
                maximum = CFDZCMAX
        """
        func = self.thdll.TH260_SetSyncCFD
        func.restype = ctypes.c_int
        level = ctypes.c_int(level['mV'])
        crossing = ctypes.c_int(zero_crossing['mV'])
        output = yield func(self.device_index, level, crossing)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(14, "set_sync_edge_trigger", level='w[mV]', edge='w')
    def set_sync_edge_trigger(self, c, level, edge):
        """
        level: Trigger level in millivolts
               minimum = CFDLVLMIN
               maximum = CFDLVLMAX
        edge: Trigger edge
               0 = falling
               1 = rising
        """
        func = self.thdll.TH260_SetSyncEdgeTrg
        func.restype = ctypes.c_int
        level = ctypes.c_int(level['mV'])
        edge = ctypes.c_int(edge)
        output = yield func(self.device_index, level, edge)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(15, "set_sync_channel_offset", offset='w[ps]')
    def set_sync_channel_offset(self, c, offset):
        """
        value: sync timing offset in ps
               minimum = CHANOFFSMIN
               maximum = CHANOFFSMAX
        """
        func = self.thdll.TH260_SetSyncChannelOffset
        func.restype = ctypes.c_int
        offset = ctypes.c_int(offset['ps'])
        output = yield func(self.device_index, offset)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(16, "set_input_cfd", channel='w', level='w[mV]', zerox='w[mV]')
    def set_input_cfd(self, c, channel, level, zerox):
        """
        level:  CFD discriminator level in millivolts
                minimum = CFDLVLMIN
                maximum = CFDLVLMAX
        zerox: CFD zero cross level in millivolts
                minimum = CFDZCMIN
                maximum = CFDZCMAX
        """
        func = self.thdll.TH260_SetInputCFD
        func.restype = ctypes.c_int
        channel = ctypes.c_int(channel)
        level = ctypes.c_int(level['mV'])
        zerox = ctypes.c_int(zerox['mV'])
        output = yield func(self.device_index, channel, level, zerox)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(18)
    def set_input_channel_offset(self, c, channel='w', value='w[ps]'):
        """
        channel: input channel index 0..1
        level: CFD discriminator level in millivolts
               minimum = DISCRMIN
               maximum = DISCRMAX
        edge: Trigger edge
               0 = falling
               1 = rising
        Note: The maximum channel index must correspond to nchannels-1 as obtained through TH260_GetNumOfInputChannels().
        """
        func = self.thdll.TH260_SetInputChannelOffset
        func.restype = ctypes.c_int
        channel = ctypes.c_int(channel)
        value = ctypes.c_int(value['ps'])
        output = yield func(self.device_index, channel, value)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(19)
    def set_input_channel_enable(self, c, channel='w', enable='w'):
        """

        """
        func = self.thdll.TH260_SetInputChannelEnable
        func.restype = ctypes.c_int
        channel = ctypes.c_int(channel)
        enable = ctypes.c_int(enable)
        output = yield func(self.device_index, channel, enable)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(20)
    def set_input_dead_time(self, c, channel='w', tdcode='w'):
        """
        The maximum channel index must correspond to nchannels-1 as obtained through TH260_GetNumOfInputChannels().
        The codes 0..7 correspond to approximate deadtimes of 24, 44, 66, 88 112, 135, 160 and 180 ns. Exact values are subject
        to production tolerances on the order of 10%. This feature is not available in boards produced before April 2015 but can be
        upgraded on request. The main purpose is that of suppressing artefacts (afterpulsing) produced by some types of detectors.
        Whether or not a given board supports this feature can be checked via TH260_GetFeatures and the bit mask FEA-
        TURE_PROG_TD as defined in thdefin.h. Note that the programmable deadtime is not available for the sync input.
        """
        func = self.thdll.TH260_SetInputDeadTime
        func.restype = ctypes.c_int
        channel = ctypes.c_int(channel)
        tdcode = ctypes.c_int(tdcode)
        output = yield func(self.device_index, channel, tdcode)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(21, stop_ovfl='w', stopcount='w')
    def SetStopOverflow(self, c, stop_ovfl, stopcount):
        """

        """
        func = self.thdll.TH260_SetStopOverflow
        func.restype = ctypes.c_int
        stop_ovfl = ctypes.c_int(stop_ovfl)
        stopcount = ctypes.c_uint(stopcount)
        output = yield func(self.device_index, stop_ovfl, stopcount)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(22, binning='w')
    def set_binning(self, c, binning):
        """

        """
        func = self.thdll.TH260_SetBinning
        func.restype = ctypes.c_int
        binning = ctypes.c_int(binning)
        output = yield func(self.device_index, binning)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(23, offset='w[ns]')
    def set_offset(self, c, offset):
        """

        """
        func = self.thdll.TH260_SetOffset
        func.restype = ctypes.c_int
        offset = ctypes.c_int(offset['ns'])
        output = yield func(self.device_index, offset)
        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(24, lencode='w', returns='w')
    def set_histo_len(self, c, lencode):
        """

        """
        func = self.thdll.TH260_
        func.restype = ctypes.c_int
        lencode = ctypes.c_int(lencode)
        actuallen = ctypes.c_int()*1024*(2**lencode)
        output = yield func(self.device_index, lencode, actuallen)

        if output == 0:
            returnValue(actuallen.value)
        else:
            returnValue('Failure')

    @setting(25)
    def clear_hist_mem(self, c):
        """

        """
        func = self.thdll.TH260_ClearHistMem
        func.restype = ctypes.c_int
        output = yield func(self.device_index)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(26, period='w[ns]')
    def set_trigger_output(self, c, period):
        """

        """
        func = self.thdll.TH260_SetTriggerOutput
        func.restype = ctypes.c_int
        period = ctypes.c_int(period['ns'])
        output = yield func(self.device_index, period)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(27, measurecontrol='w', startedge='w', stopedge='w')
    def set_measure_control(self, c, measurecontrol, startedge, stopedge):
        """

        """
        func = self.thdll.TH260_SetMeasControl
        func.restype = ctypes.c_int
        measurecontrol = ctypes.c_int(measurecontrol)
        startedge = ctypes.c_int(startedge)
        stopedge = ctypes.c_int(stopedge)
        output = yield func(self.device_index, measurecontrol, startedge, stopedge)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(28, tacq='w[ms]')
    def start_measure(self, c, tacq):
        """

        """
        func = self.thdll.TH260_StartMeas
        func.restype = ctypes.c_int
        tacq = ctypes.c_int(tacq['ms'])
        output = yield func(self.device_index, tacq)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(29)
    def stop_measure(self, c):
        """

        """
        func = self.thdll.TH260_StopMeas
        func.restype = ctypes.c_int
        output = yield func(self.device_index)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(30)
    def ctc_status(self, c):
        """

        """
        func = self.thdll.TH260_CTCStatus
        func.restype = ctypes.c_int
        ctcstatus = ctypes.c_int()
        output = yield func(self.device_index, ctcstatus)

        if output == 0:
            returnValue(ctcstatus.value)
        else:
            returnValue('Failure')

    @setting(31, channel='w', clear='w')
    def get_histogram(self, c, channel, clear):
        """

        """
        func = self.thdll.TH260_GetHistogram
        func.restype = ctypes.c_int
        channel = ctypes.c_int(channel)
        clear = ctypes.c_int(clear)
        chcount = ctypes.c_uint()*self.histo_len
        output = yield func(self.device_index, chcount, channel, clear)

        if output == 0:
            returnValue(np.array(chcount))
        else:
            returnValue('Failure')

    @setting(32)
    def get_resolution(self, c):
        """

        """
        func = self.thdll.TH260_GetResolution
        func.restype = ctypes.c_int
        resolution = ctypes.c_double()
        output = yield func(self.device_index, resolution)

        if output == 0:
            returnValue(resolution.value)
        else:
            returnValue('Failure')

    @setting(33)
    def get_sync_rate(self, c):
        """

        """
        func = self.thdll.TH260_GetSyncRate
        func.restype = ctypes.c_int
        syncrate = ctypes.c_int()
        output = yield func(self.device_index, syncrate)

        if output == 0:
            returnValue(syncrate.value)
        else:
            returnValue('Failure')

    @setting(34, channel='w')
    def get_count_rate(self, c, channel):
        func = self.thdll.TH260_GetCountRate
        func.restype = ctypes.c_int
        channel = ctypes.c_int(channel)
        cntrate = ctypes.c_int()
        output = yield func(self.device_index, channel, cntrate)

        if output == 0:
            returnValue(cntrate.value)
        else:
            returnValue('Failure')

    @setting(35)
    def get_flags(self, c):
        """

        """
        func = self.thdll.TH260_GetFlags
        func.restype = ctypes.c_int
        flags = ctypes.c_int()
        output = yield func(self.device_index, flags)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(36)
    def get_elapsed_measure_time(self, c):
        """

        """
        func = self.thdll.TH260_GetElapsedMeasTime
        func.restype = ctypes.c_int
        elapsed = ctypes.c_double()
        output = yield func(self.device_index, elapsed)
        if output == 0:
            returnValue(self.U(elapsed.value, 'ms'))
        else:
            returnValue('Failure')

    @setting(37)
    def get_warnings(self, c):
        """

        """
        func = self.thdll.TH260_GetWarnings
        func.restype = ctypes.c_int
        warnings = ctypes.c_int()
        output = yield func(self.device_index, warnings)

        if output == 0:
            returnValue(warnings.value)
        else:
            returnValue('Failure')

    @setting(38)
    def get_warnings_text(self, c, warnings):
        """

        """
        func = self.thdll.TH260_GetWarningsText
        func.restype = ctypes.c_int
        text = ctypes.create_string_buffer(16384)
        warnings = ctypes.c_int(warnings)
        output = yield func(self.device_index, text, warnings)

        if output == 0:
            returnValue(text.value)
        else:
            returnValue('Failure')

    @setting(39)
    def get_hardware_debug_info(self, c):
        """

        """
        func = self.thdll.TH260_GetHardwareDebugInfo
        func.restype = ctypes.c_int
        text = ctypes.create_string_buffer(16384)
        output = yield func(self.device_index, text)

        if output == 0:
            returnValue(text.value)
        else:
            returnValue('Failure')

    @setting(40)
    def get_sync_period(self, c):
        """

        """
        func = self.thdll.TH260_GetSyncPeriod
        func.restype = ctypes.c_int
        period = ctypes.c_double()
        output = yield func(self.device_index, period)

        if output == 0:
            returnValue(output.value)
        else:
            returnValue('Failure')

    @setting(41, count='w')
    def read_fifo(self, c, count):
        """

        """
        func = self.thdll.TH260_ReadFiFo
        func.restype = ctypes.c_int
        buffer_array = ctypes.c_uint()*count
        count = ctypes.c_int(count)
        nactual = ctypes.c_int()
        output = yield func(self.device_index, buffer_array, count, nactual)
        if output == 0:
            returnValue((np.array(buffer_array), nactual.value))
        else:
            returnValue('Failure')

    @setting(42, me='*w')
    def set_marker_edges(self, c, me):
        """

        """
        func = self.thdll.TH260_SetMarkerEdges
        func.restype = ctypes.c_int
        me = [ctypes.c_int(edge) for edge in me]
        output = yield func(self.device_index, *me)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(43, en='*w')
    def set_marker_enable(self, c, en):
        """

        """
        func = self.thdll.TH260_SetMarkerEnable
        func.restype = ctypes.c_int
        en = [ctypes.c_int(enable) for enable in en]
        output = yield func(self.device_index, *en)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')

    @setting(44, holdofftime='w')
    def set_marker_hold_off_time(self, c, holdofftime):
        """

        """
        func = self.thdll.TH260_SetMarkerHoldoffTime
        func.restype = ctypes.c_int
        holdofftime = ctypes.c_int(holdofftime)
        output = yield func(self.device_index, holdofftime)

        if output == 0:
            returnValue('Success!')
        else:
            returnValue('Failure')


if __name__ == "__main__":
    from labrad import util
    util.runServer(TimeHarpServer())
