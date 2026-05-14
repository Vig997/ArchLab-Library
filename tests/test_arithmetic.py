import pyrtl

from src.arithmetic import equal, greater_than, less_than, multiply, ripple_carry_adder, saturating_incrementer


def output_of(wire, name):
    out = pyrtl.Output(len(wire), name)
    out <<= wire
    return out


def test_ripple_adder_correctness():
    pyrtl.reset_working_block()
    a = pyrtl.Input(4, "a")
    b = pyrtl.Input(4, "b")
    sum_out, carry_out = ripple_carry_adder(a, b)
    output_of(sum_out, "sum")
    output_of(carry_out, "carry")

    sim = pyrtl.Simulation()
    for av in range(16):
        for bv in range(16):
            sim.step({"a": av, "b": bv})
            total = av + bv
            assert sim.inspect("sum") == (total & 0xF)
            assert sim.inspect("carry") == ((total >> 4) & 1)


def test_comparator_correctness():
    pyrtl.reset_working_block()
    a = pyrtl.Input(4, "a")
    b = pyrtl.Input(4, "b")
    output_of(equal(a, b), "eq")
    output_of(less_than(a, b), "lt")
    output_of(greater_than(a, b), "gt")

    sim = pyrtl.Simulation()
    for av in range(16):
        for bv in range(16):
            sim.step({"a": av, "b": bv})
            assert sim.inspect("eq") == int(av == bv)
            assert sim.inspect("lt") == int(av < bv)
            assert sim.inspect("gt") == int(av > bv)


def test_saturating_incrementer():
    pyrtl.reset_working_block()
    value = pyrtl.Input(4, "value")
    output_of(saturating_incrementer(value), "out")

    sim = pyrtl.Simulation()
    for input_value, expected in [(0, 1), (7, 8), (14, 15), (15, 15)]:
        sim.step({"value": input_value})
        assert sim.inspect("out") == expected


def test_multiply_wrapper():
    pyrtl.reset_working_block()
    a = pyrtl.Input(4, "a")
    b = pyrtl.Input(4, "b")
    output_of(multiply(a, b), "product")

    sim = pyrtl.Simulation()
    for av, bv in [(0, 9), (3, 4), (7, 8), (15, 15)]:
        sim.step({"a": av, "b": bv})
        assert sim.inspect("product") == av * bv
