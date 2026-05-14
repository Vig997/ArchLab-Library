"""Basic PyRTL building blocks used in the project."""

import math
from typing import Iterable, Optional, Tuple

import pyrtl


def _as_wire(value, bitwidth: Optional[int] = None) -> pyrtl.WireVector:
    if isinstance(value, pyrtl.WireVector):
        return value
    if bitwidth is None:
        bitwidth = max(1, int(value).bit_length())
    return pyrtl.Const(value, bitwidth=bitwidth)


def _zero(width: int) -> pyrtl.Const:
    return pyrtl.Const(0, bitwidth=width)


def _value_width(value) -> int:
    if isinstance(value, pyrtl.WireVector):
        return len(value)
    return max(1, int(value).bit_length())


def _coerce_values(*values) -> Tuple[pyrtl.WireVector, ...]:
    width = max(_value_width(value) for value in values)
    return tuple(_as_wire(value, width) for value in values)


def _trunc(value: pyrtl.WireVector, width: int) -> pyrtl.WireVector:
    """Return the lowest width bits of value."""

    return value[:width]


def register(value, name: Optional[str] = None) -> pyrtl.Register:
    """Create a register whose next value is always ``value``."""

    value = _as_wire(value)
    reg = pyrtl.Register(bitwidth=len(value), name=name)
    reg.next <<= value
    return reg


def enabled_register(value, enable, name: Optional[str] = None) -> pyrtl.Register:
    """Create a register that loads ``value`` only when ``enable`` is high."""

    value = _as_wire(value)
    enable = _as_wire(enable, 1)
    reg = pyrtl.Register(bitwidth=len(value), name=name)
    reg.next <<= pyrtl.select(enable, value, reg)
    return reg


def resettable_register(
    value,
    reset,
    reset_value: int = 0,
    enable=None,
    name: Optional[str] = None,
) -> pyrtl.Register:
    """Create a register with synchronous reset and optional enable."""

    value = _as_wire(value)
    reset = _as_wire(reset, 1)
    reg = pyrtl.Register(bitwidth=len(value), name=name)
    reset_wire = pyrtl.Const(reset_value, bitwidth=len(value))

    if enable is None:
        next_value = pyrtl.select(reset, reset_wire, value)
    else:
        enable = _as_wire(enable, 1)
        enabled_next = pyrtl.select(enable, value, reg)
        next_value = pyrtl.select(reset, reset_wire, enabled_next)

    reg.next <<= next_value
    return reg


def n_bit_counter(
    width: int,
    enable=1,
    reset=None,
    max_value: Optional[int] = None,
    name: Optional[str] = None,
) -> pyrtl.Register:
    """Create an unsigned counter.

    If ``max_value`` is omitted, the counter naturally wraps by bitwidth.
    If ``max_value`` is provided, the counter wraps to zero after that value.
    """

    enable = _as_wire(enable, 1)
    count = pyrtl.Register(bitwidth=width, name=name)
    one = pyrtl.Const(1, bitwidth=width)

    if max_value is None:
        incremented = _trunc(count + one, width)
    else:
        incremented = pyrtl.select(
            count == pyrtl.Const(max_value, bitwidth=width),
            _zero(width),
            _trunc(count + one, width),
        )

    next_value = pyrtl.select(enable, incremented, count)
    if reset is not None:
        reset = _as_wire(reset, 1)
        next_value = pyrtl.select(reset, _zero(width), next_value)

    count.next <<= next_value
    return count


def up_down_counter(
    width: int,
    up,
    enable=1,
    reset=None,
    name: Optional[str] = None,
) -> pyrtl.Register:
    """Create a counter that increments when ``up`` is high and decrements otherwise."""

    up = _as_wire(up, 1)
    enable = _as_wire(enable, 1)
    count = pyrtl.Register(bitwidth=width, name=name)
    one = pyrtl.Const(1, bitwidth=width)
    inc = _trunc(count + one, width)
    dec = _trunc(count - one, width)
    changed = pyrtl.select(up, inc, dec)
    next_value = pyrtl.select(enable, changed, count)

    if reset is not None:
        reset = _as_wire(reset, 1)
        next_value = pyrtl.select(reset, _zero(width), next_value)

    count.next <<= next_value
    return count


def mux2(sel, a, b) -> pyrtl.WireVector:
    """Two-input mux.  Returns ``a`` when sel is 0 and ``b`` when sel is 1."""

    sel = _as_wire(sel, 1)
    a, b = _coerce_values(a, b)
    return pyrtl.select(sel, b, a)


def mux4(sel, a, b, c, d) -> pyrtl.WireVector:
    """Four-input mux using a two-bit select signal."""

    sel = _as_wire(sel, 2)
    a, b, c, d = _coerce_values(a, b, c, d)
    low = mux2(sel[0], a, b)
    high = mux2(sel[0], c, d)
    return mux2(sel[1], low, high)


def demux2(sel, data) -> Tuple[pyrtl.WireVector, pyrtl.WireVector]:
    """Route data to output 0 or output 1.  The unused output is zero."""

    sel = _as_wire(sel, 1)
    data = _as_wire(data)
    zero = _zero(len(data))
    return pyrtl.select(sel, zero, data), pyrtl.select(sel, data, zero)


def demux4(sel, data) -> Tuple[pyrtl.WireVector, pyrtl.WireVector, pyrtl.WireVector, pyrtl.WireVector]:
    """Route data to one of four outputs.  Unused outputs are zero."""

    sel = _as_wire(sel, 2)
    data = _as_wire(data)
    zero = _zero(len(data))
    return tuple(
        pyrtl.select(sel == pyrtl.Const(i, bitwidth=2), data, zero)
        for i in range(4)
    )


def decoder(value, output_width: Optional[int] = None) -> pyrtl.WireVector:
    """Decode a binary value into a one-hot vector."""

    value = _as_wire(value)
    if output_width is None:
        output_width = 2 ** len(value)

    result = _zero(output_width)
    for i in range(output_width):
        result = pyrtl.select(
            value == pyrtl.Const(i, bitwidth=len(value)),
            pyrtl.Const(1 << i, bitwidth=output_width),
            result,
        )
    return result


def priority_encoder(value) -> Tuple[pyrtl.WireVector, pyrtl.WireVector]:
    """Return the highest asserted bit index and a valid flag."""

    value = _as_wire(value)
    index_width = max(1, math.ceil(math.log2(len(value))))
    encoded = pyrtl.Const(0, bitwidth=index_width)
    for i in range(len(value)):
        encoded = pyrtl.select(
            value[i],
            pyrtl.Const(i, bitwidth=index_width),
            encoded,
        )
    valid = value != _zero(len(value))
    return encoded, valid


def simple_shifter(value, amount, direction: str = "left") -> pyrtl.WireVector:
    """Shift ``value`` by ``amount``.

    ``direction`` may be ``"left"``, ``"right"``, or ``"arith_right"``.
    """

    value = _as_wire(value)
    amount = _as_wire(amount)
    if direction == "left":
        return _trunc(pyrtl.shift_left_logical(value, amount), len(value))
    if direction == "right":
        return pyrtl.shift_right_logical(value, amount)
    if direction == "arith_right":
        return pyrtl.shift_right_arithmetic(value, amount)
    raise ValueError("direction must be 'left', 'right', or 'arith_right'")


def mux_by_index(index, choices: Iterable[pyrtl.WireVector], width: Optional[int] = None) -> pyrtl.WireVector:
    """Select one wire from a Python iterable using a PyRTL index wire."""

    choices = list(choices)
    if not choices:
        raise ValueError("mux_by_index needs at least one choice")
    index = _as_wire(index)
    if width is None:
        width = len(choices[0])

    result = _zero(width)
    for i, choice in enumerate(choices):
        choice = _as_wire(choice, width)
        result = pyrtl.select(index == pyrtl.Const(i, bitwidth=len(index)), choice, result)
    return result
