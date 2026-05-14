"""Valid/ready pipeline demo."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pyrtl

from src.dataflow import connect_ready_to_input, data_buffer, source_channel


def main():
    pyrtl.reset_working_block()
    source = source_channel(8, "src")
    stage = data_buffer(source, 8, "stage")
    connect_ready_to_input(stage, "sink_ready")

    out_data = pyrtl.Output(8, "out_data")
    out_valid = pyrtl.Output(1, "out_valid")
    src_ready = pyrtl.Output(1, "src_ready")
    out_data <<= stage.data
    out_valid <<= stage.valid
    src_ready <<= source.ready

    sim = pyrtl.Simulation()
    sequence = [
        {"src_data": 5, "src_valid": 1, "sink_ready": 0},
        {"src_data": 0, "src_valid": 0, "sink_ready": 0},
        {"src_data": 0, "src_valid": 0, "sink_ready": 1},
        {"src_data": 9, "src_valid": 1, "sink_ready": 1},
    ]
    for cycle, inputs in enumerate(sequence):
        sim.step(inputs)
        print(
            f"cycle {cycle}: ready={sim.inspect('src_ready')} "
            f"valid={sim.inspect('out_valid')} data={sim.inspect('out_data')}"
        )


if __name__ == "__main__":
    main()
