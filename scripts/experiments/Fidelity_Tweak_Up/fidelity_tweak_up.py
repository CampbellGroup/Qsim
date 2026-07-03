# -*- coding: utf-8 -*-

import labrad
from Qsim.scripts.pulse_sequences.fidelity_tweak_up import FidelityTweakUp as sequence
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
import numpy as np
from labrad.units import WithUnit as U
from twisted.internet.defer import inlineCallbacks, returnValue


class FidelityTweakUp(QsimExperiment):
    """
    Performs a continuous state preparation and measurement experiment of the ion. This experiment's paramters can be
    modified on the fly, for use in tuning the fidelity of the ion.

    This experiment has been modified to be exclusively used with standard I = 1/2 qubit state readout, and a separate
    experiment is written for Shelving readout of the qubit.

    Pulse sequence diagram (369DP, 935SP, and 976SP always on):

    Standard:
        DopplerCoolingSP |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁|████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁
        StateDetectionSP |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████|▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        OpticalPumpingSP |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁|▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        760SP/760SP2     |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁|████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████|▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          StandardSD   DC          BSP*        StandardSD

    FiberEOM:
        SynthHD          |▁▁▁▁▁▁▁▁▁▁▁▁████████████████████████|▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        SynthNV          |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁|▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        760SP/760SP2     |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁|████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████|▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          StandardSD   DC          BSP*        StandardSD

    *The BrightStatePumping subsequence shown above is for Doppler-cooling-based pumping. In general, a microwave pulse is
    usually used to perform the pumping operation
    """

    name = "Fidelity Tweak Up"

    exp_parameters = []

    exp_parameters.append(("Pi_times", "qubit_0"))
    exp_parameters.append(("Pi_times", "qubit_plus"))
    exp_parameters.append(("Pi_times", "qubit_minus"))
    exp_parameters.append(("Modes", "state_detection_mode"))
    exp_parameters.append(("Modes", "bright_state_pumping"))
    exp_parameters.append(("MicrowaveInterrogation", "repetitions"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel"))
    exp_parameters.append(("MicrowaveInterrogation", "AC_line_trigger"))
    exp_parameters.append(("MicrowaveInterrogation", "delay_from_line_trigger"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel_1_Power"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel_2_Power"))
    exp_parameters.append(("StandardStateDetection", "repetitions"))
    exp_parameters.append(("StandardStateDetection", "points_per_histogram"))
    exp_parameters.append(("StandardStateDetection", "state_readout_threshold"))
    exp_parameters.extend(sequence.all_required_parameters())

    # hide some parameters
    exp_parameters.remove(("MicrowaveInterrogation", "detuning"))
    exp_parameters.remove(("MicrowaveInterrogation", "duration"))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.context = context
        #### 2/9/26 ###
        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            self.AWG_inst = self.cxn.awg_server  # connect to DAC server
            self.AWG_inst.select_device(0)
            self.AWG_windows = self.cxn.awg_windows_server
        ##############

    def run(self, cxn, context):

        qubit = self.p["Line_Selection.qubit"]
        reps = self.p["MicrowaveInterrogation.repetitions"]

        if qubit == "qubit_plus":
            pi_time = self.p["Pi_times.qubit_plus"]
            center = self.p["Transitions.qubit_plus"]
        elif qubit == "qubit_minus":
            pi_time = self.p["Pi_times.qubit_minus"]
            center = self.p["Transitions.qubit_minus"]
        else:
            pi_time = self.p["Pi_times.qubit_0"]
            center = self.p["Transitions.qubit_0"]

        self.p["MicrowaveInterrogation.duration"] = reps * pi_time
        self.p["MicrowaveInterrogation.detuning"] = U(0.0, "kHz")
        self.p["Modes.state_detection_mode"] = "Standard"

        #### 2/23/26 ###
        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
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
            self.AWG_play_signals()

        self.pulser.line_trigger_state(
            self.p["MicrowaveInterrogation.AC_line_trigger"] == "On"
        )
        self.pulser.line_trigger_duration(
            self.p["MicrowaveInterrogation.delay_from_line_trigger"]
        )
        self.setup_prob_datavault()
        i = 0
        self.program_pulser(sequence)
        while True:
            i += 1
            points_per_hist = self.p["StandardStateDetection.points_per_histogram"]
            [counts_bright, counts_dark] = self.run_sequence(max_runs=500, num=2)

            if i % points_per_hist == 0:
                hist_bright = self.process_data(counts_bright)
                hist_dark = self.process_data(counts_dark)
                self.plot_hist(hist_bright)
                self.plot_hist(hist_dark)

            self.plot_prob(i, counts_bright, counts_dark)
            should_break = self.update_progress(np.random.random())
            old_params = dict(self.p.items())
            if should_break:
                break
            self.reload_all_parameters()
            self.p = self.parameters
            if self.p != old_params:
                self.program_pulser(sequence)

        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            self.AWG_play_signals(False)

    def setup_prob_datavault(self):
        self.dv.cd(["", "fidelity_tweak_up"], True)

        self.dataset_prob = self.dv.new(
            "fidelity_tweak_up",
            [("run", "prob")],
            [
                ("Prob", "bright_prep", "num"),
                ("Prob", "dark_prep", "num"),
                ("Prob", "contrast", "num"),
            ],
        )
        self.grapher.plot(self.dataset_prob, "Fidelity", False)
        for parameter in self.p:
            self.dv.add_parameter(parameter, self.p[parameter])

    def plot_prob(self, num, counts_dark, counts_bright):
        prob_dark = self.get_pop(counts_dark)
        prob_bright = self.get_pop(counts_bright)
        self.dv.add(num, prob_dark, prob_bright, prob_bright - prob_dark)

    @inlineCallbacks
    def init_AWG(self, channel, power, other_channel_off=True):
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


if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    experiment = FidelityTweakUp(cxn=cxn)
    ident = scanner.register_external_launch(experiment.name)
    experiment.execute(ident)
