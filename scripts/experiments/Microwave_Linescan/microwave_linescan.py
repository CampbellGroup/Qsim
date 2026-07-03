# -*- coding: utf-8 -*-

import labrad
from Qsim.scripts.pulse_sequences.microwave_point.microwave_point import (
    MicrowavePoint as sequence,
)
from Qsim.scripts.pulse_sequences.ramsey_microwave_line_scan_point import (
    RamseyMicrowaveLineScanPoint as ramsey_scan,
)
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np
from scipy.optimize import curve_fit as fit
from twisted.internet.defer import inlineCallbacks, returnValue


class MicrowaveLineScan(QsimExperiment):
    """
    Scan 12.6 GHz microwave source over the qubit transition.

    Pulse sequence diagram:

    Standard:
        369SP            |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁████████████
        DopplerCoolingSP |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        StateDetectionSP |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        OpticalPumpingSP |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        MicrowaveTTL     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁██████████▁▁▁▁▁▁▁▁▁▁▁▁
        Microwave_qubit  |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▓▓▓▓▓▓▓▓▓▓▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁████████████
        760SP/760SP2     |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          MI          StandardSD

    FiberEOM:
        369SP            |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁████████████
        SynthHD          |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁████████████
        SynthNV          |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        MicrowaveTTL     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁██████████▁▁▁▁▁▁▁▁▁▁▁▁
        Microwave_qubit  |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▓▓▓▓▓▓▓▓▓▓▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁████████████
        760SP/760SP2     |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          MI          StandardSD
    """

    name = "Microwave Line Scan"

    exp_parameters = []
    exp_parameters.append(("DopplerCooling", "detuning"))
    exp_parameters.append(("Transitions", "main_cooling_369"))

    exp_parameters.append(("MicrowaveLinescan", "scan"))
    exp_parameters.append(("MicrowaveLinescan", "linescan_type"))

    exp_parameters.append(("Pi_times", "qubit_0"))
    exp_parameters.append(("Pi_times", "qubit_plus"))
    exp_parameters.append(("Pi_times", "qubit_minus"))
    exp_parameters.append(("Pi_times", "simultaneous"))

    exp_parameters.extend(sequence.all_required_parameters())
    exp_parameters.extend(ramsey_scan.all_required_parameters())
    exp_parameters.remove(("MicrowaveInterrogation", "detuning"))
    exp_parameters.remove(("MicrowaveInterrogation", "duration"))
    exp_parameters.remove(("MicrowaveInterrogation", "microwave_source"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel_1_Power"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel_2_Power"))
    exp_parameters.append(("MicrowaveInterrogation", "AC_line_trigger"))
    exp_parameters.append(("MicrowaveInterrogation", "delay_from_line_trigger"))

    exp_parameters.append(("bf_fluorescence", "crop_start_time"))
    exp_parameters.append(("bf_fluorescence", "crop_stop_time"))

    exp_parameters.append(("Modes", "state_detection_mode"))
    exp_parameters.append(("ShelvingStateDetection", "repetitions"))
    exp_parameters.append(("StandardStateDetection", "repetitions"))
    exp_parameters.append(("StandardStateDetection", "points_per_histogram"))
    exp_parameters.append(("StandardStateDetection", "state_readout_threshold"))
    exp_parameters.append(("Shelving_Doppler_Cooling", "doppler_counts_threshold"))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        #### 2/9/26 ###
        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            self.AWG_inst = self.cxn.awg_server  # connect to DAC server
            self.AWG_inst.select_device(0)
            self.AWG_windows = self.cxn.awg_windows_server
        ##############

    def run(self, cxn, context):

        data = self.setup_datavault(
            "frequency", "probability"
        )  # gives the x and y names to Data Vault
        qubit = self.p["Line_Selection.qubit"]

        if qubit in ["qubit_0", "qubit_plus", "qubit_minus"]:
            self.setup_grapher("Microwave Linescan " + qubit)
        else:
            self.setup_grapher("Microwave Linescan " + "qubit_0")

        self.detunings = self.get_scan_list(self.p["MicrowaveLinescan.scan"], "kHz")
        mode = self.p["Modes.state_detection_mode"]
        self.pulser.line_trigger_state(
            self.p["MicrowaveInterrogation.AC_line_trigger"] == "On"
        )
        self.pulser.line_trigger_duration(
            self.p["MicrowaveInterrogation.delay_from_line_trigger"]
        )

        linescan_type = self.p["MicrowaveLinescan.linescan_type"]

        if qubit == "qubit_0":
            center = self.p["Transitions.qubit_0"]
            pi_time = self.p["Pi_times.qubit_0"]

        elif qubit == "qubit_plus":
            center = self.p["Transitions.qubit_plus"]
            pi_time = self.p["Pi_times.qubit_plus"]

        elif qubit == "qubit_minus":
            center = self.p["Transitions.qubit_minus"]
            pi_time = self.p["Pi_times.qubit_minus"]

        elif qubit == "minus_plus":
            pi_time = self.p["Pi_times.simultaneous"]

        #### 2/9/26 ###
        # if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
        #     print('AWG mode')
        #     freq = self.p["ddsDefaults.qubit_dds_freq"] - ( self.p["MicrowaveInterrogation.detuning"] + center )
        #     channel = self.p["MicrowaveInterrogation.AWG_Channel"]
        #     AWG_power = self.p["MicrowaveInterrogation.AWG_Channel_" + channel + "_Power"]
        #     print("power", AWG_power)
        #     print("channel", channel)
        #     self.init_AWG(channel=channel, power= AWG_power)
        #     self.AWG_play_signals()

        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            print("AWG mode")
            if qubit == "qubit_0":
                center = self.p["Transitions.qubit_0"]
            elif qubit == "qubit_plus":
                center = self.p["Transitions.qubit_plus"]
            elif qubit == "qubit_minus":
                center = self.p["Transitions.qubit_minus"]

            if qubit in ["qubit_0", "qubit_plus", "qubit_minus"]:
                freq = self.p["ddsDefaults.qubit_dds_freq"] - (
                    self.p["MicrowaveInterrogation.detuning"] + center
                )
                channel = self.p["MicrowaveInterrogation.AWG_Channel"]
                AWG_power = self.p[
                    "MicrowaveInterrogation.AWG_Channel_" + channel + "_Power"
                ]
                self.init_AWG(channel=channel, power=AWG_power)
                self.AWG_load_waveform(
                    channel=channel, frequency=freq, waveform="HP_microwave"
                )

            elif qubit == "minus_plus":
                freq_minus = self.p["ddsDefaults.qubit_dds_freq"] - (
                    self.p["MicrowaveInterrogation.detuning"]
                    + self.p["Transitions.qubit_minus"]
                )
                freq_plus = self.p["ddsDefaults.qubit_dds_freq"] - (
                    self.p["MicrowaveInterrogation.detuning"]
                    + self.p["Transitions.qubit_plus"]
                )
                center = self.p["Transitions.qubit_plus"]
                AWG_power_1 = self.p["MicrowaveInterrogation.AWG_Channel_1_Power"]
                AWG_power_2 = self.p["MicrowaveInterrogation.AWG_Channel_2_Power"]
                self.init_AWG(channel=1, power=AWG_power_1)
                self.init_AWG(channel=2, power=AWG_power_2, other_channel_off=False)
                self.AWG_load_waveform(
                    channel=1, frequency=freq_minus, waveform="minus"
                )
                # self.AWG_load_waveform(channel=2, frequency=freq_plus, waveform='plus')

            self.AWG_play_signals()

        ##############

        self.p["MicrowaveInterrogation.duration"] = pi_time
        deltas, probs = [], []
        for i, detuning in enumerate(self.detunings):
            should_break = self.update_progress(i / float(len(self.detunings)))
            if should_break:
                break

            self.p["MicrowaveInterrogation.detuning"] = U(detuning, "kHz")

            # 2/13 #
            if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
                if qubit in ["qubit_0", "qubit_plus", "qubit_minus"]:
                    self.AWG_load_waveform(
                        channel=channel,
                        frequency=freq - self.p["MicrowaveInterrogation.detuning"],
                        waveform="HP_microwave",
                    )
                elif qubit == "minus_plus":
                    self.AWG_load_waveform(
                        channel=2,
                        frequency=freq_plus - self.p["MicrowaveInterrogation.detuning"],
                        waveform="plus",
                    )
            #########

            if linescan_type == "Rabi":
                self.program_pulser(sequence)
            if linescan_type == "Ramsey":
                self.program_pulser(ramsey_scan)

            if mode == "Shelving":
                [doppler_counts, detection_counts] = self.run_sequence(
                    max_runs=500, num=2
                )
                errors = np.where(
                    doppler_counts
                    <= self.p["Shelving_Doppler_Cooling.doppler_counts_threshold"]
                )
                counts = np.delete(detection_counts, errors)
            if mode == "Standard":
                [counts] = self.run_sequence()
            if mode == "StandardFiberEOM":
                [counts] = self.run_sequence()

            if i % self.p["StandardStateDetection.points_per_histogram"] == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)

            pop = self.get_pop(counts)
            self.dv.add(detuning + center["kHz"], pop)
            deltas.append(detuning + center["kHz"])
            probs.append(pop)

        if qubit != "qubit_0":
            param_guess = [
                20.0,
                deltas[np.argmax(probs)],
                np.min(probs),
                np.max(probs) - np.min(probs),
            ]
            popt, pcov = fit(self.sinc_fit, deltas, probs, p0=param_guess)

            if qubit in ["qubit_0", "qubit_plus", "qubit_minus"]:
                self.pv.set_parameter(("Transitions", qubit, U(popt[1], "kHz")))
                print(
                    "Updated " + str(qubit) + " frequency to " + str(popt[1]) + " kHz"
                )

        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            self.AWG_play_signals(False)

    def finalize(self, cxn, context):
        self.pulser.line_trigger_state(False)
        pass

    def sinc_fit(self, freq, omega, center, offset, scale):
        """
        This fits the sinc function created in an interleaved linescan,
        identical to the fit function in RealSimpleGrapher
        """
        return (
            scale
            * (omega**2 / (omega**2 + (center - freq) ** 2))
            * np.sin(np.sqrt(omega**2 + (center - freq) ** 2) * np.pi / (2 * omega))
            ** 2
            + offset
        )

    @inlineCallbacks
    def init_AWG(self, channel, power, other_channel_off=True):
        # yield self.AWG_inst.compile_basic_waveform(frequency["Hz"], waveform) # compile basic waveform
        channel = int(channel)
        yield self.AWG_inst.change_amplitude(
            channel, power["dBm"]
        )  # change power of waveform
        yield self.AWG_inst.rf_channel_state(channel, True)
        if other_channel_off:
            yield self.AWG_inst.rf_channel_state(channel % 2 + 1, False)
        yield self.AWG_inst.channel_run_mode(channel, "Continuous")

    @inlineCallbacks
    def AWG_load_waveform(self, channel, frequency, waveform):
        # yield self.AWG_inst.compile_basic_waveform(frequency["Hz"], waveform) # compile basic waveform
        channel = int(channel)
        yield self.AWG_windows.make_multitone_text(
            [0], frequency["Hz"], 16000000000, waveform
        )
        yield self.AWG_inst.text_to_waveform(waveform)
        yield self.AWG_inst.assign_waveform_to_channel(
            channel, waveform
        )  # load waveform to channel 1

    @inlineCallbacks
    def AWG_play_signals(self, play_state=True):
        yield self.AWG_inst.play_signals(play_state)

    ##################

if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveLineScan(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
