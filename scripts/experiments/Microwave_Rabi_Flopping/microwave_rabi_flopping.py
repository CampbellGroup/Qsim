# -*- coding: utf-8 -*-

import labrad
from Qsim.scripts.pulse_sequences.microwave_point.microwave_point import (
    MicrowavePoint as sequence,
)
from Qsim.scripts.experiments.qsimexperiment import QsimExperiment
from labrad.units import WithUnit as U
import numpy as np
from twisted.internet.defer import inlineCallbacks, returnValue


class MicrowaveRabiFlopping(QsimExperiment):
    """
    repeatedly prepare the |0> state, interrogate with resonant microwaves for
    a variable time t and measure the population in the bright state

    Pulse sequence diagram:

    Standard:
        369SP            |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁████████████
        DopplerCoolingSP |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        StateDetectionSP |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
        OpticalPumpingSP |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        MicrowaveTTL     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁██████████▁▁▁▁▁▁▁▁▁▁▁▁
        Microwave_qubit  |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁██████████▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁████████████
        760SP/760SP2     |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          MI~~~~~~~~~~StandardSD

    FiberEOM:
        369SP            |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁████████████
        SynthHD          |▁▁▁▁▁▁▁▁▁▁▁▁████████████████████████████████████
        SynthNV          |▁▁▁▁▁▁▁▁▁▁▁▁████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        MicrowaveTTL     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁██████████▁▁▁▁▁▁▁▁▁▁▁▁
        Microwave_qubit  |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁██████████▁▁▁▁▁▁▁▁▁▁▁▁
        935SP/976SP      |████████████████████████▁▁▁▁▁▁▁▁▁▁▁▁████████████
        760SP/760SP2     |████████████▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁
        ReadoutCount     |▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁████████████
             (TurnOffAll) DC          OP          MI~~~~~~~~~~StandardSD
    """

    name = "Microwave Rabi Flopping"

    exp_parameters = []
    exp_parameters.append(("RabiFlopping", "scan"))
    exp_parameters.append(("DopplerCooling", "detuning"))
    exp_parameters.append(("Transitions", "main_cooling_369"))
    exp_parameters.append(("Modes", "bright_state_pumping"))

    exp_parameters.append(("Modes", "state_detection_mode"))
    exp_parameters.append(("ShelvingStateDetection", "repetitions"))
    exp_parameters.append(("StandardStateDetection", "repetitions"))
    exp_parameters.append(("StandardStateDetection", "points_per_histogram"))
    exp_parameters.append(("StandardStateDetection", "state_readout_threshold"))
    exp_parameters.append(("Shelving_Doppler_Cooling", "doppler_counts_threshold"))
    exp_parameters.append(("MicrowaveInterrogation", "AC_line_trigger"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel_1_Power"))
    exp_parameters.append(("MicrowaveInterrogation", "AWG_Channel_2_Power"))

    exp_parameters.extend(sequence.all_required_parameters())

    exp_parameters.remove(("MicrowaveInterrogation", "duration"))

    def initialize(self, cxn, context, ident):
        self.ident = ident
        self.pulser = cxn.pulser
        self.pzt_server = cxn.piezo_server
        self.cavity_channel = 1
        self.cavity_voltage = 0.0
        self.counts_track_mean = 0.0
        #### 2/9/26 ###
        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            self.AWG_inst = self.cxn.awg_server  # connect to DAC server
            self.AWG_inst.select_device(0)
            self.AWG_windows = self.cxn.awg_windows_server
        ##############

    def run(self, cxn, context):

        self.cavity_voltage = self.pzt_server.get_voltage(self.cavity_channel)

        qubit = self.p["Line_Selection.qubit"]
        mode = self.p["Modes.state_detection_mode"]

        init_bright_state_pumping_method = self.p["Modes.bright_state_pumping"]
        init_microwave_pulse_sequence = self.p["MicrowaveInterrogation.pulse_sequence"]
        init_optical_pumping_method = self.p["OpticalPumping.method"]

        self.p["BrightStatePumping.method"] = "Microwave"
        # self.p['BrightStatePumping.method'] = 'Doppler Cooling Fiber EOM'

        # self.p['MicrowaveInterrogation.pulse_sequence'] = 'standard'

        self.pulser.line_trigger_state(
            self.p["MicrowaveInterrogation.AC_line_trigger"] == "On"
        )

        self.setup_datavault(
            "time", "probability"
        )  # gives the x and y names to Data Vault

        #### 2/9/26 ###
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
                print("ch pow:", AWG_power)
                print("freq :", freq)

            elif qubit == "minus_plus":
                # freq_minus = self.p["ddsDefaults.qubit_dds_freq"] - ( self.p["MicrowaveInterrogation.detuning"] + self.p["Transitions.qubit_minus"] )
                # freq_plus = self.p["ddsDefaults.qubit_dds_freq"] - ( self.p["MicrowaveInterrogation.detuning"] + self.p["Transitions.qubit_plus"] )
                # AWG_power_1 = self.p["MicrowaveInterrogation.AWG_Channel_1_Power"]
                # AWG_power_2 = self.p["MicrowaveInterrogation.AWG_Channel_2_Power"]
                # self.init_AWG(channel=1, power=AWG_power_1)
                # self.init_AWG(channel=2, power=AWG_power_2, other_channel_off=False)
                # self.AWG_load_waveform(channel=1, frequency=freq_plus, waveform='plus')
                # self.AWG_load_waveform(channel=2, frequency=freq_minus, waveform='minus')
                freq_minus = self.p["ddsDefaults.qubit_dds_freq"] - (
                    self.p["MicrowaveInterrogation.detuning"]
                    + self.p["Transitions.qubit_minus"]
                )
                freq_plus = self.p["ddsDefaults.qubit_dds_freq"] - (
                    self.p["MicrowaveInterrogation.detuning"]
                    + self.p["Transitions.qubit_plus"]
                )
                freq0 = self.p["ddsDefaults.qubit_dds_freq"] - (
                    self.p["MicrowaveInterrogation.detuning"]
                    + self.p["Transitions.qubit_0"]
                )
                AWG_power_1 = self.p["MicrowaveInterrogation.AWG_Channel_1_Power"]
                AWG_power_2 = self.p["MicrowaveInterrogation.AWG_Channel_2_Power"]
                self.init_AWG(channel=1, power=AWG_power_1)
                self.init_AWG(channel=2, power=AWG_power_2, other_channel_off=False)
                self.AWG_load_waveform(
                    channel=1, frequency=freq_minus, waveform="minus"
                )
                # self.AWG_load_waveform(channel=2, frequency=freq_plus, waveform='plus')
                self.AWG_load_waveform(channel=2, frequency=freq0, waveform="zero")

            self.AWG_play_signals()

        ##############

        if mode == "Shelving":
            self.setup_shelving_rabi_datavault()
        else:
            self.setup_datavault("time", "probability")
        # self.setup_grapher("Rabi Flopping " + qubit)
        self.setup_grapher(
            "Rabi Flopping " + "qubit_0"
        )  # hack to view minus plus rabi flopping, temp

        self.times = self.get_scan_list(self.p["RabiFlopping.scan"], "us")

        for i, duration in enumerate(self.times):
            should_break = self.update_progress(i / float(len(self.times)))
            if should_break:
                self.pulser.line_trigger_state(False)
                break
            self.p["MicrowaveInterrogation.duration"] = U(duration, "us")
            # if mode == 'Standard':
            #     # force standard optical pumping if standard readout method used
            #     # no sense in quadrupole optical pumping by accident if using standard readout
            #     self.p['OpticalPumping.method'] = 'Standard'

            self.program_pulser(sequence)
            if mode == "Shelving":
                [doppler_counts, detection_counts] = self.run_sequence(
                    max_runs=500, num=2
                )
                errors = np.where(
                    doppler_counts
                    <= self.p["Shelving_Doppler_Cooling.doppler_counts_threshold"]
                )
                counts = np.delete(detection_counts, errors)
                countsDopFixed = np.delete(doppler_counts, errors)
            else:
                [counts] = self.run_sequence()

            if i % self.p["StandardStateDetection.points_per_histogram"] == 0:
                hist = self.process_data(counts)
                self.plot_hist(hist)

            pop = self.get_pop(counts)
            if mode == "Shelving":
                self.dv.add(
                    i, duration, pop, len(counts), context=self.shelving_context
                )
            else:
                self.dv.add(duration, pop)

            if mode == "Shelving":
                if i == 1:
                    self.counts_track_mean = np.mean(countsDopFixed)
                    print(
                        "mean doppler counts on first experiment is  = "
                        + str(self.counts_track_mean)
                    )
                elif i > 1:
                    diff = np.mean(countsDopFixed) - self.counts_track_mean
                    if np.abs(diff) > 7.0:
                        self.cavity_voltage = (
                            self.cavity_voltage + np.sign(diff) * 0.005
                        )
                        if np.sign(diff) * 0.005 < 0.2:
                            self.pzt_server.set_voltage(
                                self.cavity_channel, U(self.cavity_voltage, "V")
                            )
                            print(
                                "Updated cavity voltage to "
                                + str(self.cavity_voltage)
                                + " V"
                            )
                    else:
                        pass

        # reset all the init settings that you forced for this experiment
        self.p["BrightStatePumping.method"] = init_bright_state_pumping_method
        self.p["MicrowaveInterrogation.pulse_sequence"] = init_microwave_pulse_sequence
        self.p["OpticalPumping.method"] = init_optical_pumping_method
        self.pulser.line_trigger_state(False)

        if self.p["MicrowaveInterrogation.microwave_source"] == "AWG":
            self.AWG_play_signals(False)

    def setup_shelving_rabi_datavault(self):

        self.shelving_context = self.dv.context()
        self.dv.cd(["", "rabi_flopping_shelving"], True, context=self.shelving_context)
        self.hf_dark_dataset = self.dv.new(
            "counts",
            [("run", "arb")],
            [
                ("time", "time", "num"),
                ("prob", "prob", "num"),
                ("experiments", "experiments", "num"),
            ],
            context=self.shelving_context,
        )
        for parameter in self.p:
            self.dv.add_parameter(
                parameter, self.p[parameter], context=self.shelving_context
            )

    def finalize(self, cxn, context):
        pass

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

    # @inlineCallbacks
    # def terminate_AWG(self):
    #     yield self.AWG_inst.play_signals(False)


if __name__ == "__main__":
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = MicrowaveRabiFlopping(cxn=cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
