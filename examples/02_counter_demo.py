"""Counter demo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrtl

from src.primitives import n_bit_counter


def main():
    pyrtl.reset_working_block()
    enable = pyrtl.Input(1, "enable")
    count = pyrtl.Output(4, "count")
    count <<= n_bit_counter(4, enable=enable, name="demo_count")

    sim = pyrtl.Simulation()
    for cycle, en in enumerate([1, 1, 1, 0, 1, 1]):
        sim.step({"enable": en})
        print(f"cycle {cycle}: enable={en}, count={sim.inspect('count')}")


if __name__ == "__main__":
    main()
