"""Fork, mux, and demux dataflow demo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrtl

from src.dataflow import connect_ready_to_input, demux_actor, fork2, mux_actor, source_channel


def main():
    pyrtl.reset_working_block()
    fork_source = source_channel(8, "fork_src")
    fork_out0, fork_out1 = fork2(fork_source, 8, "fork")
    connect_ready_to_input(fork_out0, "fork_ready0")
    connect_ready_to_input(fork_out1, "fork_ready1")

    sel = pyrtl.Input(1, "sel")
    mux_in0 = source_channel(8, "mux_in0")
    mux_in1 = source_channel(8, "mux_in1")
    muxed = mux_actor(sel, mux_in0, mux_in1, 8, "muxed")
    demux_out0, demux_out1 = demux_actor(sel, muxed, 8, "demuxed")
    connect_ready_to_input(demux_out0, "demux_ready0")
    connect_ready_to_input(demux_out1, "demux_ready1")

    fork_ready = pyrtl.Output(1, "fork_ready")
    fork0_valid = pyrtl.Output(1, "fork0_valid")
    fork1_valid = pyrtl.Output(1, "fork1_valid")
    demux0_valid = pyrtl.Output(1, "demux0_valid")
    demux1_valid = pyrtl.Output(1, "demux1_valid")
    demux0_data = pyrtl.Output(8, "demux0_data")
    demux1_data = pyrtl.Output(8, "demux1_data")
    fork_ready <<= fork_source.ready
    fork0_valid <<= fork_out0.valid
    fork1_valid <<= fork_out1.valid
    demux0_valid <<= demux_out0.valid
    demux1_valid <<= demux_out1.valid
    demux0_data <<= demux_out0.data
    demux1_data <<= demux_out1.data

    sim = pyrtl.Simulation()
    for inputs in [
        {
            "fork_src_data": 33,
            "fork_src_valid": 1,
            "fork_ready0": 1,
            "fork_ready1": 1,
            "sel": 0,
            "mux_in0_data": 10,
            "mux_in0_valid": 1,
            "mux_in1_data": 20,
            "mux_in1_valid": 1,
            "demux_ready0": 1,
            "demux_ready1": 1,
        },
        {
            "fork_src_data": 44,
            "fork_src_valid": 1,
            "fork_ready0": 1,
            "fork_ready1": 0,
            "sel": 1,
            "mux_in0_data": 10,
            "mux_in0_valid": 1,
            "mux_in1_data": 20,
            "mux_in1_valid": 1,
            "demux_ready0": 1,
            "demux_ready1": 1,
        },
    ]:
        sim.step(inputs)
        print(
            inputs,
            "->",
            {
                "fork_ready": sim.inspect("fork_ready"),
                "fork_valids": (sim.inspect("fork0_valid"), sim.inspect("fork1_valid")),
                "demux0": (sim.inspect("demux0_valid"), sim.inspect("demux0_data")),
                "demux1": (sim.inspect("demux1_valid"), sim.inspect("demux1_data")),
            },
        )


if __name__ == "__main__":
    main()
