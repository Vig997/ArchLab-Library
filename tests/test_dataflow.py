import pyrtl

from src.dataflow import (
    connect_ready_to_input,
    data_buffer,
    demux_actor,
    fork2,
    mux_actor,
    priority_merge_actor,
    source_channel,
)


def output_of(wire, name):
    out = pyrtl.Output(len(wire), name)
    out <<= wire
    return out


def test_valid_ready_pipeline_behavior():
    pyrtl.reset_working_block()
    source = source_channel(8, "src")
    stage = data_buffer(source, 8, "stage")
    connect_ready_to_input(stage, "sink_ready")
    output_of(source.ready, "src_ready")
    output_of(stage.data, "out_data")
    output_of(stage.valid, "out_valid")

    sim = pyrtl.Simulation()
    sim.step({"src_data": 7, "src_valid": 1, "sink_ready": 0})
    assert sim.inspect("src_ready") == 1
    assert sim.inspect("out_valid") == 0

    sim.step({"src_data": 0, "src_valid": 0, "sink_ready": 0})
    assert sim.inspect("src_ready") == 0
    assert sim.inspect("out_valid") == 1
    assert sim.inspect("out_data") == 7

    sim.step({"src_data": 0, "src_valid": 0, "sink_ready": 1})
    assert sim.inspect("out_valid") == 1
    assert sim.inspect("out_data") == 7

    sim.step({"src_data": 0, "src_valid": 0, "sink_ready": 0})
    assert sim.inspect("out_valid") == 0


def test_fork_behavior():
    pyrtl.reset_working_block()
    source = source_channel(8, "src")
    out0, out1 = fork2(source, 8, "fork")
    connect_ready_to_input(out0, "ready0")
    connect_ready_to_input(out1, "ready1")
    output_of(source.ready, "src_ready")
    output_of(out0.valid, "valid0")
    output_of(out1.valid, "valid1")
    output_of(out0.data, "data0")
    output_of(out1.data, "data1")

    sim = pyrtl.Simulation()
    sim.step({"src_data": 42, "src_valid": 1, "ready0": 1, "ready1": 0})
    assert sim.inspect("src_ready") == 0
    assert sim.inspect("valid0") == 0
    assert sim.inspect("valid1") == 0

    sim.step({"src_data": 42, "src_valid": 1, "ready0": 1, "ready1": 1})
    assert sim.inspect("src_ready") == 1
    assert sim.inspect("valid0") == 1
    assert sim.inspect("valid1") == 1
    assert sim.inspect("data0") == 42
    assert sim.inspect("data1") == 42


def test_mux_demux_dataflow_behavior():
    pyrtl.reset_working_block()
    sel = pyrtl.Input(1, "sel")
    in0 = source_channel(8, "in0")
    in1 = source_channel(8, "in1")
    muxed = mux_actor(sel, in0, in1, 8, "muxed")
    out0, out1 = demux_actor(sel, muxed, 8, "demuxed")
    connect_ready_to_input(out0, "ready0")
    connect_ready_to_input(out1, "ready1")

    output_of(in0.ready, "in0_ready")
    output_of(in1.ready, "in1_ready")
    output_of(out0.valid, "out0_valid")
    output_of(out1.valid, "out1_valid")
    output_of(out0.data, "out0_data")
    output_of(out1.data, "out1_data")

    sim = pyrtl.Simulation()
    sim.step(
        {
            "sel": 0,
            "in0_data": 5,
            "in0_valid": 1,
            "in1_data": 9,
            "in1_valid": 1,
            "ready0": 1,
            "ready1": 1,
        }
    )
    assert sim.inspect("in0_ready") == 1
    assert sim.inspect("in1_ready") == 0
    assert sim.inspect("out0_valid") == 1
    assert sim.inspect("out1_valid") == 0
    assert sim.inspect("out0_data") == 5

    sim.step(
        {
            "sel": 1,
            "in0_data": 5,
            "in0_valid": 1,
            "in1_data": 9,
            "in1_valid": 1,
            "ready0": 1,
            "ready1": 1,
        }
    )
    assert sim.inspect("in0_ready") == 0
    assert sim.inspect("in1_ready") == 1
    assert sim.inspect("out0_valid") == 0
    assert sim.inspect("out1_valid") == 1
    assert sim.inspect("out1_data") == 9


def test_priority_merge_behavior():
    pyrtl.reset_working_block()
    in0 = source_channel(8, "in0")
    in1 = source_channel(8, "in1")
    merged = priority_merge_actor(in0, in1, 8, "merged")
    connect_ready_to_input(merged, "sink_ready")

    output_of(in0.ready, "in0_ready")
    output_of(in1.ready, "in1_ready")
    output_of(merged.valid, "out_valid")
    output_of(merged.data, "out_data")

    sim = pyrtl.Simulation()
    sim.step(
        {
            "in0_data": 100,
            "in0_valid": 1,
            "in1_data": 200,
            "in1_valid": 1,
            "sink_ready": 1,
        }
    )
    assert sim.inspect("out_valid") == 1
    assert sim.inspect("out_data") == 100
    assert sim.inspect("in0_ready") == 1
    assert sim.inspect("in1_ready") == 0

    sim.step(
        {
            "in0_data": 100,
            "in0_valid": 0,
            "in1_data": 200,
            "in1_valid": 1,
            "sink_ready": 1,
        }
    )
    assert sim.inspect("out_valid") == 1
    assert sim.inspect("out_data") == 200
    assert sim.inspect("in0_ready") == 1
    assert sim.inspect("in1_ready") == 1
