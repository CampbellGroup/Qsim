"""
### BEGIN NODE INFO
[info]
name = AWG Server
version = 1.3
description = 


[startup]
cmdline = %PYTHON% %FILE%
timeout = 20

[shutdown]
message = 987654321
timeout = 5
### END NODE INFO
"""

import numpy as np
from labrad.server import setting
import labrad.units as _units
from labrad.gpib import GPIBManagedServer, GPIBDeviceWrapper
from twisted.internet.defer import inlineCallbacks, returnValue

from labrad.units import WithUnit as U


def boolean_to_on_off_string(boolean):
    """
    takes a boolean and converts True to 'On' and False to 'Off' for string based GPIB commands
    :param boolean:
    :return: string, 'On' or 'Off'
    """
    if boolean:
        return "ON"
    else:
        return "OFF"


class AWGWrapper(GPIBDeviceWrapper):

    @inlineCallbacks
    def BasicWaveFormSettings(
        self,
        HzFrequency,
        function="sine",
        auto="len",
        Cycles="250",
        length="2.4E3",
        Amp="0.5",
        Offset="0.0",
        sample_rate="16E9",
    ):
        """
        Changes settings in the AWG basic waveform editor plug in. Waveform will still need to be compiled after this.
        All arguments should be passed as strings.
        :param HzFrequency: frequency in Hz
        :param function: 'sine', 'square', 'triangle', 'ramp', 'Noise', or 'DC'
        :param auto: parameter to be auto calculated: 'len', 'cycle', 'freq'
        :param Cycles: number of cycles in waveform
        :param length: length of waveform in samples
        :param Amp: in volts
        :param Offset: in volts
        :param sample_rate: max of 16 GSamples/s

        :return:
        """
        Basic_WaveForm_Settings = (
            "BWaveform:Function "
            + function
            + "; Auto "
            + auto
            + "; SRate "
            + sample_rate
            + "; Amplitude "
            + Amp
            + "; Offset "
            + Offset
        )
        if auto == "len":
            Basic_WaveForm_Settings += (
                "; Cycle " + Cycles + "; Frequency " + HzFrequency
            )
        elif auto == "cycle":
            Basic_WaveForm_Settings += (
                "; Length " + length + "; Frequency " + HzFrequency
            )
        elif auto == "freq":
            Basic_WaveForm_Settings += "; Length " + length + "; Cycle " + Cycles
        else:
            print("Warning: Invalid auto parameter. Check Compiled Waveform.")
        yield self.write(Basic_WaveForm_Settings)

    @inlineCallbacks
    def CompileSettings(self, WaveFormName):
        """
        Sets name and auto-load settings for the waveform compiler.
        :param WaveFormName: name to give to compiled waveform
        :return:
        """
        compile_settings = (
            "BWaveform:Compile:Name '" + WaveFormName + "';CAssign 0"
        )  # set the name of the waveform we are creating and set it to not automatically load onto one of the channels
        yield self.write(compile_settings)

    @inlineCallbacks
    def CompileBasicWaveForm(self):
        """
        Compiles the waveform in the basic wave form editor plug in.
        :return:
        """
        yield self.write("BWaveform:Compile")

    @inlineCallbacks
    def RFChannelState(self, channel, state):
        """
        Switches the specified channel output state (on or off).
        :param channel: 1 or 2 to specify the channel
        :param state: True for output on
        :return:
        """
        output = "Output" + channel + ":State " + state
        yield self.write(output)

    @inlineCallbacks
    def AssingWaveformToChannel(self, channel, waveform_name):
        """
        Takes a waveform from the waveform list and loads it onto the specified channel.
        :param channel: 1 or 2 to specify the channel
        :param waveform_name: Name of the waveform in the waveform list.
        :return:
        """
        assign = "Source" + channel + ":Casset:Waveform '" + waveform_name + "'"
        yield self.write(assign)
        time_out = U(20, "s")
        yield self.query("*OPC?", timeout=time_out)  # command to load text to waveform

    @inlineCallbacks
    def SetNormalization(self, normalization_type):
        """
        Sets normalization method to use when loading text files as waveforms.
        :param normalization_type: 'NONE', 'FScale' (scales to amplitude), 'ZReference' (preserves offset)
        :return:
        """
        yield self.write(
            "MMemory:Open:Normalize " + normalization_type
        )  # set normalization of text files

    @inlineCallbacks
    def LoadWaveformFromText(self, file_path):
        """
        Loads a text folder to a waveform. Be sure that the text file was written assuming the current sample rate used.
        :param file_path: path on the AWG computer to the text file to be loaded
        :return:
        """
        # load_waveform = "MMEMORY:OPEN:TXT '"+ file_path +"',ANALog\n*OPC?" # command to load text to waveform
        load_waveform = "MMEMORY:OPEN:TXT '" + file_path + "',ANALog"
        yield self.write(load_waveform)  # load waveform from text
        # yield self.timeout(1)
        # yield self.query("*OPC?") # command to load text to waveform
        time_out = U(20.0, "s")
        yield self.query("*OPC?", timeout=time_out)  # command to load text to waveform

    @inlineCallbacks
    def ChangeAmplitude(self, channel, V_amplitude):
        """
        Changes the peak to peak voltage amplitude of the specified channel.
        :param channel: 1 or 2
        :param V_amplitude: peak to peak voltage in volts
        :return:
        """
        power = "Source" + channel + ":Voltage:Level:Immediate:Amplitude " + V_amplitude
        yield self.write(power)

    @inlineCallbacks
    def AllOutputsOff(self, state):
        """
        Switches all outputs off if True
        :param state: switches outputs off if True
        :return:
        """
        yield self.write("Output:Off " + state)

    @inlineCallbacks
    def ChannelRunMode(self, channel, mode):
        """
        Sets the run mode of the specified channel with respect to triggering.
        :param channel: 1 or 2
        :param mode: 'triggered', 'TContinuous', or 'Continuous'
        :return:
        """
        run_mode = "Source" + channel + ":RMODE " + mode
        yield self.write(run_mode)

    @inlineCallbacks
    def PlaySignals(self, state):
        """
        Plays signals on both channels if True
        :param state: Plays signals if True
        :return:
        """
        if state:
            yield self.write("AWGControl:Run:Immediate")
        else:
            yield self.write("AWGControl:Stop:Immediate")

    @inlineCallbacks
    def Command(self, command):
        """
        Sends a command to the AWG
        :param command (string): command to be sent to the AWG
        :return:
        """
        yield self.write(command)

    @inlineCallbacks
    def Query(self, query, timeout=U(60.0, "s")):
        # yield print(self.query(query, timeout=timeout))
        # tmp clayton edit
        yield print(self.query(query))


class AWGServer(GPIBManagedServer):
    name = "AWG Server"  # Server name
    deviceName = "TEKTRONIX AWG70002B"  # Model string returned from *IDN?
    deviceWrapper = AWGWrapper

    @setting(3331, "compile_basic_waveform", Hz_frequency="v", waveform_name="s")
    def compile_basic_waveform(self, c, Hz_frequency, waveform_name):
        """
        Uses the built-in basic waveform editor plug in to make single frequencies sine wave.
        :param Hz_frequency (float): frequency of desired signal
        :param waveform_name (string): name of waveform
        :return:
        """
        dev = self.selectedDevice(c)
        freq, waveform_name = str(Hz_frequency), str(waveform_name)
        print(type(Hz_frequency), type(freq))
        print(Hz_frequency, freq)
        yield dev.BasicWaveFormSettings(freq)
        yield dev.CompileSettings(waveform_name)
        yield dev.CompileBasicWaveForm()

    @setting(3332, "rf channel state", channel="i", state="b")
    def rf_channel_state(self, c, channel, state):
        """
        On/Off switch for the specified channel.
        :param state (booleanb): True for on
        :param channel (int): channel to switch (either 1 or 2)
        :return:
        """
        dev = self.selectedDevice(c)
        channel = str(int(channel))
        state = boolean_to_on_off_string(state)
        yield dev.RFChannelState(channel, state)

    @setting(3333, "assign waveform to channel", channel="i", waveform_name="s")
    def assign_waveform_to_channel(self, c, channel, waveform_name):
        """
        Assigns a waveform from the waveform list (not just a text file) to a channel of the AWG (1 or 2).
        :param waveform_name (string): name of waveform in waveform list (must already be compiled)
        :param channel (int): channel number 1 or 2
        :return:
        """
        dev = self.selectedDevice(c)
        waveform_name, channel = str(waveform_name), str(int(channel))
        yield dev.AssingWaveformToChannel(channel, waveform_name)

    @setting(3334, "text to waveform", waveform_name="s", waveform_path="s")
    def text_to_waveform(self, c, waveform_name, waveform_path=None):
        """
        Converts text file on the AWG computer to a waveform and loads it to the waveform list.
        Be cautious that the current sample rate on the AWG is the same as that used when creating
        the text file, or the frequencies will be incorrect.
        :param waveform_name (string): name of the text file to load (ex: 'MAOP_Tones')
        :param waveform_path (string): path to where the waveform is, will default to "C:/Users/tek_local_admin/Documents/WaveForm/"
        :return:
        """
        dev = self.selectedDevice(c)
        if waveform_name[-4:] not in [".txt", ".TXT"]:
            waveform_name += ".txt"
        yield dev.SetNormalization("FScale")
        if waveform_path is None:
            waveform_path = "C:/Users/tek_local_admin/Documents/WaveForm/"
        yield dev.LoadWaveformFromText(waveform_path + waveform_name)

    @setting(3335, "change amplitude", channel="i", dBm_amplitude="v")
    def change_amplitude(self, c, channel, dBm_amplitude):
        """
        Changes peak to peak voltage of a waveform currently loaded on the specified channel.
        :param dBm_amplitude (float): dBm power [must be between -9 and -3)
        :param channel (int): channel to adjust the amplitude of (either 1 or 2)
        :return:
        """
        dev = self.selectedDevice(c)
        V_amplitude = np.sqrt(10 ** (dBm_amplitude / 10) * 0.53449)
        V_amplitude, channel = str(V_amplitude), str(int(channel))
        yield dev.ChangeAmplitude(channel, V_amplitude)

    @setting(3336, "all outputs off", state="b")
    def all_outputs_off(self, c, state):
        """
        Determines if 'All Outputs Off' button is on. If on, no signals will be output.
        :param state (boolean): True will turn all outputs off
        :return:
        """
        dev = self.selectedDevice(c)
        state = boolean_to_on_off_string(state)
        yield dev.AllOutputsOff(state)

    @setting(3337, "channel run mode", channel="i", mode="s")
    def channel_run_mode(self, c, channel, mode):
        """
        Sets the run/trigger mode for the channel.
        :param mode (string): 'triggered', 'TContinuous', 'Continuous'
        :param channel (int): channel to change run mode of (either 1 or 2)
        :return:
        """
        dev = self.selectedDevice(c)
        channel = str(int(channel))
        if mode not in ["triggered", "TContinuous", "Continuous"]:
            print(
                "Invalid run mode. Mode must be 'triggered', 'TContinuous', or 'Continuous'"
            )
        else:
            yield dev.ChannelRunMode(channel, mode)

    @setting(3338, "play signals", state="b")
    def play_signals(self, c, state):
        """
        Signals will be playing if 'ON'. If output is 'OFF', there will still be no output
        even if this function is called, it controls the large play button on the AWG GUI.
        :param state (boolean): plays signals if True
        :return:
        """
        dev = self.selectedDevice(c)
        yield dev.PlaySignals(state)

    @setting(3339, "write", command="s")
    def write(self, c, command):
        """
        Can write a string command straight to the AWG. Good for specific niche tasks or debugging.
        :param command (string): string to be sent to the AWG
        :return:
        """
        dev = self.selectedDevice(c)
        yield dev.Command(command)

    @setting(3340, "query", query="s")
    def query(self, c, query):
        dev = self.selectedDevice(c)
        yield dev.Query(query)


__server__ = AWGServer()

if __name__ == "__main__":
    from labrad import util

    util.runServer(__server__)


# ## JinXang Code ##
#
# # Wrapper #
#
#     @inlineCallbacks
#     def set_RF_state(self, value):
#         if value:
#             yield self.write("OUTPut1:STATe ON")
#         elif not value:
#             yield self.write("OUTPut1:STATe OFF")
#
#     @inlineCallbacks
#     def createWaveform(self, name, N):
#         # REAL => float32 samples
#         # Use quotes around name; ensure N matches your payload length
#         yield self.write(f'WLIST:WAVEFORM:NEW "{name}", {N}, REAL')
#
#     @inlineCallbacks
#     def setWaveformData(self, name, payload, N):
#         # payload is raw float32 LE bytes (len = 4*N)
#         L = len(payload)
#         header = f"#{len(str(L))}{L}".encode("ascii")
#         cmd = f'WLIST:WAVEFORM:DATA "{name}", 0, {N}, '.encode("ascii")
#         yield self.write_raw(cmd + header + payload)
#
#     @inlineCallbacks
#     def setWaveform(self, block):
#         yield self.write_raw(b'WLIST:WAVEFORM:DATA "Test1",0,1024,' + block)
#
#     @inlineCallbacks
#     def setClockRate(self, fs):
#         yield self.write(f"CLOCk:SRATe {fs}")
#
#     @inlineCallbacks
#     def selectWaveformOnChan(self, ch, name):
#         # Point channel to the waveform in the WLIST
#         yield self.write(f'SOURce{ch}:WAVeform "{name}"')
#
#     @inlineCallbacks
#     def stopWaveform(self):
#         """Stop the AWG playback."""
#         yield self.write("AWGControl:STOP")
#
#     @inlineCallbacks
#     def deleteWaveform(self, name):
#         """Delete a waveform from the AWG's waveform list if it exists."""
#         yield self.write(f'WLIST:WAVEFORM:DELETE "{name}"')
#
# # Server #
#
#     @setting(224, "rf_state", value="b")
#     def rf_state(self, c, value):
#         """Turns the RF state on or off."""
#         dev = self.selectedDevice(c)
#         yield dev.set_RF_state(value)
#
#     @setting(225, "create_waveform", name="s")
#     def create_waveform(self, c, name):
#         dev = self.selectedDevice(c)
#         yield dev.createWaveform(name)
#
#     @setting(300, "sine_wave", name="s", freq="v", duration="v", cycles="v")
#     def sine_wave(self, c, name, freq, duration, cycles):
#         dev = self.selectedDevice(c)
#         yield dev.createWaveform(name)
#
#     @setting(302, "run_wave_new", name="s")
#     def run_wave_new(self, c, name):
#         """
#         Build a sine at 'freq' Hz, total buffer length chosen to have 'cycles'
#         of the sine. Duration is duration seconds => N = round(Fs*duration).
#         """
#         import numpy as np
#
#         dev = self.selectedDevice(c)
#         yield dev.selectWaveformOnChan(1, name)  # assign waveform to CH1
#         yield dev.write("AWGControl:RMOD CONT")  # continuous run mode
#         yield dev.write("AWGControl:RUN")
#         # Optionally enable output:
#         yield dev.set_RF_state(True)
#
#     @setting(401, "stop_waveform")
#     def stop_waveform(self, c):
#         dev = self.selectedDevice(c)
#         yield dev.stopWaveform()
#
#     @setting(
#         301,
#         "sine_wave_new",
#         name="s",
#         freq="v",
#         duration="v",
#         cycles="v",  # dimensionless
#         Fsamp="i",
#     )
#     def sine_wave_new(self, c, name, freq, duration, cycles, Fsamp):
#         """
#         Build a sine at 'freq' Hz, total buffer length chosen to have 'cycles'
#         of the sine. Duration is duration seconds => N = round(Fs*duration).
#         """
#         import numpy as np
#
#         dev = self.selectedDevice(c)
#         Fsamp = (
#             Fsamp * 1000
#         )  # This is to mitigate the strange erro caused by "v" type data too large
#         # Fs = 25e9  # AWG70002B typical
#         Fs = Fsamp
#         N = int(round(Fs * duration))
#         if N < 2048:
#             print("N has to be larger than 2048")
#             N = 2048
#         # Force integer cycles as requested:
#         k = cycles
#         # Adjust N so f_out = Fs*k/N ~= freq (or recompute k from desired freq)
#         N = int(round(Fs * k / freq))
#         # Ensure alignment (power-of-64, etc. as required by your setup)
#         # N = max(2048, (N // 64) * 64)
#
#         # Recompute actual output frequency:
#         f_out = Fs * k / N
#         print(f_out, "Hz")
#         phi = np.pi / 2 + np.pi * k / N
#         n = np.arange(N, dtype=np.float64)
#         x = np.sin(2 * np.pi * k * n / N + phi).astype(np.float32)
#
#         payload = x.astype("<f4").tobytes()
#         print(name, N)
#         yield dev.setClockRate(Fs)
#         yield dev.deleteWaveform(name)
#         yield dev.createWaveform(name, N)
#         yield dev.setWaveformData(name, payload, N)
#         yield dev.selectWaveformOnChan(1, name)  # assign waveform to CH1
#         yield dev.write("AWGControl:RMOD CONT")  # continuous run mode
#         yield dev.write("AWGControl:RUN")
#         # Optionally enable output:
#         yield dev.set_RF_state(True)
#
#
#     @setting(226, "set_waveform")
#     def set_waveform(self, c):
#         # Continuous 100 MHz sine on AWG70000 with NO phase slip at buffer wrap.
#         # Key trick: choose k so f_out = Fs*k/N exactly AND add a phase offset φ so
#         # the first and last samples are IDENTICAL (y[0] == y[N-1]) -> seamless loop.
#
#         import numpy as np
#
#         dev = self.selectedDevice(c)
#         print("print the following")
#         # ---- Set your model's clock here ----
#         f_out = 100e6  # 100 MHz
#         Fs = 50e9  # 50e9 for AWG70001B; use 25e9 if you have AWG70002B
#         N = 8000  # multiple of 64 and >= typical LMIN (2400) length/(Fs/f_out) should be integer
#
#         # Integer cycles in buffer so f_out = Fs * k / N exactly
#         # (For Fs=50e9, f=100e6 -> Fs/f = 500; 8000/500 = 16 cycles)
#         k = int(round(f_out * N / Fs))
#         if abs(Fs * k / N - f_out) > 0.0:  # require exact (within float round-off)
#             raise ValueError(
#                 "Pick N so Fs*k/N equals f_out exactly (e.g., N multiple of Fs/f)."
#             )
#
#         # Phase offset to make wrap seamless:
#         # choose φ = π/2 + π*k/N  -> sin(φ) == sin(φ - 2πk/N)  ==> y[0] == y[N-1]
#         phi = np.pi / 2 + np.pi * k / N
#
#         n = np.arange(N, dtype=np.float64)
#         x = np.sin(2 * np.pi * k * n / N + phi).astype(
#             np.float32
#         )  # REAL samples in [-1, +1]
#
#         # IEEE-488.2 definite-length block (little-endian float32)
#         payload = x.astype("<f4").tobytes()  # 4*N bytes
#         L = len(payload)
#         block = f"#{len(str(L))}{L}".encode("ascii") + payload
#
#         # Program using ONLY wrappers you've already used
#         yield dev.setClockRate(Fs)  # CLOCK:SRATE Fs
#         yield dev.setWaveform(
#             block
#         )  # WLIST:WAVEFORM:NEW "Test1",N + DATA "Test1",0,N,#<hdr><bytes>
