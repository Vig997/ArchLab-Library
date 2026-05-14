"""Simple valid/ready dataflow blocks for learning."""

from dataclasses import dataclass
from typing import Callable, Tuple

import pyrtl


@dataclass
class DataflowSignal:
    """A simple valid/ready channel."""

    data: pyrtl.WireVector
    valid: pyrtl.WireVector
    ready: pyrtl.WireVector


def _as_wire(value, bitwidth=None) -> pyrtl.WireVector:
    if isinstance(value, pyrtl.WireVector):
        return value
    if bitwidth is None:
        bitwidth = max(1, int(value).bit_length())
    return pyrtl.Const(value, bitwidth=bitwidth)


def source_channel(width: int, name: str) -> DataflowSignal:
    """Create input data/valid wires and a ready wire driven by downstream logic."""

    return DataflowSignal(
        data=pyrtl.Input(width, f"{name}_data"),
        valid=pyrtl.Input(1, f"{name}_valid"),
        ready=pyrtl.WireVector(1, f"{name}_ready_wire"),
    )


def channel(width: int, name: str) -> DataflowSignal:
    """Create an internal dataflow channel."""

    return DataflowSignal(
        data=pyrtl.WireVector(width, f"{name}_data"),
        valid=pyrtl.WireVector(1, f"{name}_valid"),
        ready=pyrtl.WireVector(1, f"{name}_ready_wire"),
    )


def connect_ready_to_input(signal: DataflowSignal, input_name: str) -> pyrtl.Input:
    """Connect a channel ready signal to a top-level input and return that input."""

    ready = pyrtl.Input(1, input_name)
    signal.ready <<= ready
    return ready


def pass_through_stage(inp: DataflowSignal, width: int, name: str = "pass") -> DataflowSignal:
    """A combinational stage that forwards data, valid, and ready."""

    out = channel(width, name)
    out.data <<= inp.data
    out.valid <<= inp.valid
    inp.ready <<= out.ready
    return out


def data_buffer(inp: DataflowSignal, width: int, name: str = "buf") -> DataflowSignal:
    """A one-entry valid/ready buffer, also useful as a pipeline register."""

    out = channel(width, name)
    data_reg = pyrtl.Register(width, f"{name}_data_reg")
    valid_reg = pyrtl.Register(1, f"{name}_valid_reg")

    out.data <<= data_reg
    out.valid <<= valid_reg

    inp.ready <<= ~valid_reg | out.ready
    accept = inp.valid & inp.ready
    send = out.ready & valid_reg

    data_reg.next <<= pyrtl.select(accept, inp.data, data_reg)
    valid_reg.next <<= pyrtl.select(
        accept,
        pyrtl.Const(1, bitwidth=1),
        pyrtl.select(send, pyrtl.Const(0, bitwidth=1), valid_reg),
    )
    return out


def fork2(inp: DataflowSignal, width: int, name: str = "fork") -> Tuple[DataflowSignal, DataflowSignal]:
    """Duplicate one item to two outputs.

    The input is ready only when both outputs are ready.
    """

    out0 = channel(width, f"{name}_0")
    out1 = channel(width, f"{name}_1")

    both_ready = out0.ready & out1.ready
    out0.data <<= inp.data
    out1.data <<= inp.data
    out0.valid <<= inp.valid & both_ready
    out1.valid <<= inp.valid & both_ready
    inp.ready <<= both_ready
    return out0, out1


def mux_actor(sel, in0: DataflowSignal, in1: DataflowSignal, width: int, name: str = "mux") -> DataflowSignal:
    """Choose between two input channels."""

    sel = _as_wire(sel, 1)
    out = channel(width, name)
    out.data <<= pyrtl.select(sel, in1.data, in0.data)
    out.valid <<= pyrtl.select(sel, in1.valid, in0.valid)
    in0.ready <<= out.ready & ~sel
    in1.ready <<= out.ready & sel
    return out


def demux_actor(sel, inp: DataflowSignal, width: int, name: str = "demux") -> Tuple[DataflowSignal, DataflowSignal]:
    """Route an input channel to one of two output channels."""

    sel = _as_wire(sel, 1)
    out0 = channel(width, f"{name}_0")
    out1 = channel(width, f"{name}_1")

    out0.data <<= inp.data
    out1.data <<= inp.data
    out0.valid <<= inp.valid & ~sel
    out1.valid <<= inp.valid & sel
    inp.ready <<= pyrtl.select(sel, out1.ready, out0.ready)
    return out0, out1


def unit_rate_actor(
    inp: DataflowSignal,
    operation: Callable[[pyrtl.WireVector], pyrtl.WireVector],
    width: int,
    name: str = "actor",
) -> DataflowSignal:
    """Apply a simple combinational operation to each accepted item."""

    out = channel(width, name)
    out.data <<= operation(inp.data)
    out.valid <<= inp.valid
    inp.ready <<= out.ready
    return out


def priority_merge_actor(
    in0: DataflowSignal,
    in1: DataflowSignal,
    width: int,
    name: str = "merge",
) -> DataflowSignal:
    """Merge two inputs, giving priority to input 0 when both are valid."""

    out = channel(width, name)
    choose0 = in0.valid
    out.data <<= pyrtl.select(choose0, in0.data, in1.data)
    out.valid <<= in0.valid | in1.valid
    in0.ready <<= out.ready
    in1.ready <<= out.ready & ~in0.valid
    return out
