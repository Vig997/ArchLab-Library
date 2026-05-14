"""Ripple-carry adder demo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrtl

from src.arithmetic import ripple_carry_adder


def main():
    pyrtl.reset_working_block()
    a = pyrtl.Input(4, "a")
    b = pyrtl.Input(4, "b")
    sum_wire, carry_wire = ripple_carry_adder(a, b)
    sum_out = pyrtl.Output(4, "sum")
    carry_out = pyrtl.Output(1, "carry")
    sum_out <<= sum_wire
    carry_out <<= carry_wire

    sim = pyrtl.Simulation()
    for av, bv in [(2, 3), (7, 8), (15, 1)]:
        sim.step({"a": av, "b": bv})
        print(f"{av} + {bv} -> sum={sim.inspect('sum')} carry={sim.inspect('carry')}")


if __name__ == "__main__":
    main()
