"""Small memory examples for PyRTL simulations."""

import math
from dataclasses import dataclass
from typing import Dict, Optional

import pyrtl

from .primitives import mux_by_index


def _as_wire(value, bitwidth: Optional[int] = None) -> pyrtl.WireVector:
    if isinstance(value, pyrtl.WireVector):
        return value
    if bitwidth is None:
        bitwidth = max(1, int(value).bit_length())
    return pyrtl.Const(value, bitwidth=bitwidth)


def _ptr_width(depth: int) -> int:
    return max(1, math.ceil(math.log2(depth)))


def _count_width(depth: int) -> int:
    return max(1, math.ceil(math.log2(depth + 1)))


def _trunc(value: pyrtl.WireVector, width: int) -> pyrtl.WireVector:
    return value[:width]


def _inc_pointer(pointer: pyrtl.WireVector, depth: int) -> pyrtl.WireVector:
    width = len(pointer)
    wrapped = pointer == pyrtl.Const(depth - 1, bitwidth=width)
    incremented = _trunc(pointer + pyrtl.Const(1, bitwidth=width), width)
    return pyrtl.select(wrapped, pyrtl.Const(0, bitwidth=width), incremented)


@dataclass(frozen=True)
class FIFOResult:
    data_out: pyrtl.WireVector
    full: pyrtl.WireVector
    empty: pyrtl.WireVector
    count: pyrtl.WireVector


def rom_read(
    table: Dict[int, int],
    address,
    bitwidth: int,
    name: str = "rom",
) -> pyrtl.WireVector:
    """Create a small ROM and return its read data wire."""

    address = _as_wire(address)
    rom = pyrtl.RomBlock(
        bitwidth=bitwidth,
        addrwidth=len(address),
        romdata=table,
        name=name,
    )
    return rom[address]


def synchronous_ram(
    read_address,
    write_address,
    write_data,
    write_enable,
    bitwidth: int,
    addrwidth: int,
    name: str = "ram",
):
    """Create a simple RAM and return ``(read_data, mem_block)``."""

    read_address = _as_wire(read_address, addrwidth)
    write_address = _as_wire(write_address, addrwidth)
    write_data = _as_wire(write_data, bitwidth)
    write_enable = _as_wire(write_enable, 1)

    mem = pyrtl.MemBlock(bitwidth=bitwidth, addrwidth=addrwidth, name=name)
    read_data = mem[read_address]
    mem[write_address] <<= pyrtl.MemBlock.EnabledWrite(write_data, write_enable)
    return read_data, mem


def small_fifo(data_in, enqueue, dequeue, width: int, depth: int = 4, name: str = "fifo") -> FIFOResult:
    """Build a small register-based FIFO queue.

    This FIFO is for learning and simulation.  It stores ``depth`` entries in
    registers, exposes a combinational ``data_out`` for the head entry, and
    updates its head, tail, and count once per clock.
    """

    if depth < 2:
        raise ValueError("small_fifo depth must be at least 2")

    data_in = _as_wire(data_in, width)
    enqueue = _as_wire(enqueue, 1)
    dequeue = _as_wire(dequeue, 1)

    pointer_width = _ptr_width(depth)
    count_width = _count_width(depth)

    head = pyrtl.Register(bitwidth=pointer_width, name=f"{name}_head")
    tail = pyrtl.Register(bitwidth=pointer_width, name=f"{name}_tail")
    count = pyrtl.Register(bitwidth=count_width, name=f"{name}_count")
    cells = [
        pyrtl.Register(bitwidth=width, name=f"{name}_cell_{i}")
        for i in range(depth)
    ]

    full = count == pyrtl.Const(depth, bitwidth=count_width)
    empty = count == pyrtl.Const(0, bitwidth=count_width)
    can_enqueue = enqueue & ~full
    can_dequeue = dequeue & ~empty

    data_out = mux_by_index(head, cells, width)

    for i, cell in enumerate(cells):
        is_tail = tail == pyrtl.Const(i, bitwidth=pointer_width)
        cell.next <<= pyrtl.select(can_enqueue & is_tail, data_in, cell)

    head.next <<= pyrtl.select(can_dequeue, _inc_pointer(head, depth), head)
    tail.next <<= pyrtl.select(can_enqueue, _inc_pointer(tail, depth), tail)

    one = pyrtl.Const(1, bitwidth=count_width)
    plus_one = _trunc(count + one, count_width)
    minus_one = _trunc(count - one, count_width)
    enqueue_only = can_enqueue & ~can_dequeue
    dequeue_only = can_dequeue & ~can_enqueue
    count.next <<= pyrtl.select(
        enqueue_only,
        plus_one,
        pyrtl.select(dequeue_only, minus_one, count),
    )

    return FIFOResult(data_out=data_out, full=full, empty=empty, count=count)


def circular_buffer(data_in, write, read, width: int, depth: int = 4, name: str = "cbuf") -> FIFOResult:
    """A small circular buffer using the same logic as the FIFO."""

    return small_fifo(data_in, write, read, width=width, depth=depth, name=name)
