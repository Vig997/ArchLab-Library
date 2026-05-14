"""Basic mux demo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrtl

from src.primitives import mux2


def main():
    pyrtl.reset_working_block()
    sel = pyrtl.Input(1, "sel")
    a = pyrtl.Input(4, "a")
    b = pyrtl.Input(4, "b")
    out = pyrtl.Output(4, "out")
    out <<= mux2(sel, a, b)

    sim = pyrtl.Simulation()
    for inputs in [{"sel": 0, "a": 3, "b": 12}, {"sel": 1, "a": 3, "b": 12}]:
        sim.step(inputs)
        print(inputs, "-> out =", sim.inspect("out"))


if __name__ == "__main__":
    main()
