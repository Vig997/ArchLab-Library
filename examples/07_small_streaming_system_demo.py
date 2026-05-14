"""Small streaming system demo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrtl

from src.dataflow import connect_ready_to_input, data_buffer, priority_merge_actor, source_channel, unit_rate_actor


def main():
    pyrtl.reset_working_block()
    main_in = source_channel(8, "main")
    side_in = source_channel(8, "side")
    buffered = data_buffer(main_in, 8, "main_buf")
    incremented = unit_rate_actor(
        buffered,
        lambda data: (data + pyrtl.Const(1, bitwidth=8))[:8],
        8,
        "inc",
    )
    merged = priority_merge_actor(incremented, side_in, 8, "merged")
    connect_ready_to_input(merged, "sink_ready")

    out_data = pyrtl.Output(8, "out_data")
    out_valid = pyrtl.Output(1, "out_valid")
    main_ready = pyrtl.Output(1, "main_ready")
    side_ready = pyrtl.Output(1, "side_ready")
    out_data <<= merged.data
    out_valid <<= merged.valid
    main_ready <<= main_in.ready
    side_ready <<= side_in.ready

    sim = pyrtl.Simulation()
    sequence = [
        {"main_data": 4, "main_valid": 1, "side_data": 100, "side_valid": 1, "sink_ready": 1},
        {"main_data": 0, "main_valid": 0, "side_data": 100, "side_valid": 1, "sink_ready": 1},
        {"main_data": 8, "main_valid": 1, "side_data": 101, "side_valid": 1, "sink_ready": 1},
        {"main_data": 0, "main_valid": 0, "side_data": 101, "side_valid": 1, "sink_ready": 1},
    ]
    for cycle, inputs in enumerate(sequence):
        sim.step(inputs)
        print(
            f"cycle {cycle}: valid={sim.inspect('out_valid')} data={sim.inspect('out_data')} "
            f"main_ready={sim.inspect('main_ready')} side_ready={sim.inspect('side_ready')}"
        )


if __name__ == "__main__":
    main()
