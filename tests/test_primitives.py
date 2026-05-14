import pyrtl

from src.primitives import (
    decoder,
    demux2,
    demux4,
    enabled_register,
    mux2,
    mux4,
    n_bit_counter,
    priority_encoder,
    resettable_register,
    simple_shifter,
    up_down_counter,
)


def output_of(wire, name="out"):
    out = pyrtl.Output(len(wire), name)
    out <<= wire
    return out


def test_mux2_behavior():
    pyrtl.reset_working_block()
    sel = pyrtl.Input(1, "sel")
    a = pyrtl.Input(4, "a")
    b = pyrtl.Input(4, "b")
    output_of(mux2(sel, a, b))

    sim = pyrtl.Simulation()
    sim.step({"sel": 0, "a": 3, "b": 12})
    assert sim.inspect("out") == 3
    sim.step({"sel": 1, "a": 3, "b": 12})
    assert sim.inspect("out") == 12


def test_mux4_behavior():
    pyrtl.reset_working_block()
    sel = pyrtl.Input(2, "sel")
    out = mux4(sel, 1, 2, 3, 4)
    output_of(out)

    sim = pyrtl.Simulation()
    for sel_value, expected in enumerate([1, 2, 3, 4]):
        sim.step({"sel": sel_value})
        assert sim.inspect("out") == expected


def test_demux_behavior():
    pyrtl.reset_working_block()
    sel = pyrtl.Input(1, "sel")
    data = pyrtl.Input(4, "data")
    out0, out1 = demux2(sel, data)
    output_of(out0, "out0")
    output_of(out1, "out1")

    sim = pyrtl.Simulation()
    sim.step({"sel": 0, "data": 9})
    assert sim.inspect("out0") == 9
    assert sim.inspect("out1") == 0
    sim.step({"sel": 1, "data": 9})
    assert sim.inspect("out0") == 0
    assert sim.inspect("out1") == 9


def test_demux4_behavior():
    pyrtl.reset_working_block()
    sel = pyrtl.Input(2, "sel")
    data = pyrtl.Input(4, "data")
    outs = demux4(sel, data)
    for i, wire in enumerate(outs):
        output_of(wire, f"out{i}")

    sim = pyrtl.Simulation()
    for selected in range(4):
        sim.step({"sel": selected, "data": 11})
        for i in range(4):
            assert sim.inspect(f"out{i}") == (11 if i == selected else 0)


def test_counter_behavior():
    pyrtl.reset_working_block()
    enable = pyrtl.Input(1, "enable")
    count = n_bit_counter(3, enable=enable, name="count")
    output_of(count, "count_out")

    sim = pyrtl.Simulation()
    seen = []
    for en in [1, 1, 0, 1, 1]:
        sim.step({"enable": en})
        seen.append(sim.inspect("count_out"))
    assert seen == [0, 1, 2, 2, 3]


def test_up_down_counter_behavior():
    pyrtl.reset_working_block()
    up = pyrtl.Input(1, "up")
    enable = pyrtl.Input(1, "enable")
    count = up_down_counter(3, up=up, enable=enable, name="count")
    output_of(count, "count_out")

    sim = pyrtl.Simulation()
    seen = []
    for values in [
        {"up": 1, "enable": 1},
        {"up": 1, "enable": 1},
        {"up": 0, "enable": 1},
        {"up": 0, "enable": 1},
        {"up": 0, "enable": 0},
    ]:
        sim.step(values)
        seen.append(sim.inspect("count_out"))
    assert seen == [0, 1, 2, 1, 0]


def test_register_helpers():
    pyrtl.reset_working_block()
    value = pyrtl.Input(4, "value")
    enable = pyrtl.Input(1, "enable")
    reset = pyrtl.Input(1, "reset")
    en_reg = enabled_register(value, enable, name="en_reg")
    rst_reg = resettable_register(value, reset, reset_value=3, name="rst_reg")
    output_of(en_reg, "en_out")
    output_of(rst_reg, "rst_out")

    sim = pyrtl.Simulation()
    sim.step({"value": 5, "enable": 1, "reset": 0})
    assert sim.inspect("en_out") == 0
    assert sim.inspect("rst_out") == 0
    sim.step({"value": 9, "enable": 0, "reset": 1})
    assert sim.inspect("en_out") == 5
    assert sim.inspect("rst_out") == 5
    sim.step({"value": 2, "enable": 0, "reset": 0})
    assert sim.inspect("en_out") == 5
    assert sim.inspect("rst_out") == 3


def test_decoder_priority_encoder_and_shifter():
    pyrtl.reset_working_block()
    value = pyrtl.Input(4, "value")
    amount = pyrtl.Input(2, "amount")
    output_of(decoder(value[:2]), "decoded")
    encoded, valid = priority_encoder(value)
    output_of(encoded, "encoded")
    output_of(valid, "valid")
    output_of(simple_shifter(value, amount, "left"), "left")
    output_of(simple_shifter(value, amount, "right"), "right")

    sim = pyrtl.Simulation()
    for input_value in range(16):
        for shift in range(4):
            sim.step({"value": input_value, "amount": shift})
            assert sim.inspect("decoded") == (1 << (input_value & 0b11))
            assert sim.inspect("encoded") == (0 if input_value == 0 else input_value.bit_length() - 1)
            assert sim.inspect("valid") == int(input_value != 0)
            assert sim.inspect("left") == ((input_value << shift) & 0b1111)
            assert sim.inspect("right") == (input_value >> shift)
