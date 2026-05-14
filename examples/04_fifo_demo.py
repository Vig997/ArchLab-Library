"""Small FIFO demo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrtl

from src.memory import small_fifo


def main():
    pyrtl.reset_working_block()
    data_in = pyrtl.Input(8, "data_in")
    enqueue = pyrtl.Input(1, "enqueue")
    dequeue = pyrtl.Input(1, "dequeue")
    fifo = small_fifo(data_in, enqueue, dequeue, width=8, depth=4)

    data_out = pyrtl.Output(8, "data_out")
    empty = pyrtl.Output(1, "empty")
    full = pyrtl.Output(1, "full")
    count = pyrtl.Output(3, "count")
    data_out <<= fifo.data_out
    empty <<= fifo.empty
    full <<= fifo.full
    count <<= fifo.count

    sim = pyrtl.Simulation()
    sequence = [
        {"data_in": 10, "enqueue": 1, "dequeue": 0},
        {"data_in": 20, "enqueue": 1, "dequeue": 0},
        {"data_in": 0, "enqueue": 0, "dequeue": 1},
        {"data_in": 0, "enqueue": 0, "dequeue": 0},
    ]
    for cycle, inputs in enumerate(sequence):
        sim.step(inputs)
        print(
            f"cycle {cycle}: out={sim.inspect('data_out')} "
            f"empty={sim.inspect('empty')} full={sim.inspect('full')} count={sim.inspect('count')}"
        )


if __name__ == "__main__":
    main()
