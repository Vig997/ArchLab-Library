"""Small arithmetic circuits written in PyRTL."""

from typing import Optional, Tuple

import pyrtl


def _as_wire(value, bitwidth: Optional[int] = None) -> pyrtl.WireVector:
    if isinstance(value, pyrtl.WireVector):
        return value
    if bitwidth is None:
        bitwidth = max(1, int(value).bit_length())
    return pyrtl.Const(value, bitwidth=bitwidth)


def _trunc(value: pyrtl.WireVector, width: int) -> pyrtl.WireVector:
    return value[:width]


def half_adder(a, b) -> Tuple[pyrtl.WireVector, pyrtl.WireVector]:
    """One-bit half adder."""

    a = _as_wire(a, 1)
    b = _as_wire(b, 1)
    sum_bit = a ^ b
    carry = a & b
    return sum_bit, carry


def full_adder(a, b, carry_in) -> Tuple[pyrtl.WireVector, pyrtl.WireVector]:
    """One-bit full adder."""

    first_sum, first_carry = half_adder(a, b)
    sum_bit, second_carry = half_adder(first_sum, carry_in)
    carry_out = first_carry | second_carry
    return sum_bit, carry_out


def ripple_carry_adder(a, b, carry_in=0) -> Tuple[pyrtl.WireVector, pyrtl.WireVector]:
    """Add two same-width unsigned values with a ripple-carry structure."""

    a = _as_wire(a)
    b = _as_wire(b, len(a))
    carry = _as_wire(carry_in, 1)
    sum_bits = []

    for i in range(len(a)):
        sum_bit, carry = full_adder(a[i], b[i], carry)
        sum_bits.append(sum_bit)

    if len(sum_bits) == 1:
        return sum_bits[0], carry
    return pyrtl.concat(*reversed(sum_bits)), carry


def subtractor(a, b) -> pyrtl.WireVector:
    """Unsigned subtractor that returns the low bits of ``a - b``."""

    a = _as_wire(a)
    b = _as_wire(b, len(a))
    return _trunc(a - b, len(a))


def equal(a, b) -> pyrtl.WireVector:
    """Equality comparator."""

    a = _as_wire(a)
    b = _as_wire(b, len(a))
    return a == b


def less_than(a, b) -> pyrtl.WireVector:
    """Unsigned less-than comparator."""

    a = _as_wire(a)
    b = _as_wire(b, len(a))
    return a < b


def greater_than(a, b) -> pyrtl.WireVector:
    """Unsigned greater-than comparator."""

    a = _as_wire(a)
    b = _as_wire(b, len(a))
    return a > b


def saturating_incrementer(value, max_value: Optional[int] = None) -> pyrtl.WireVector:
    """Increment unless the value is already at the saturation point."""

    value = _as_wire(value)
    width = len(value)
    if max_value is None:
        max_value = (1 << width) - 1
    at_max = value >= pyrtl.Const(max_value, bitwidth=width)
    incremented = _trunc(value + pyrtl.Const(1, bitwidth=width), width)
    return pyrtl.select(at_max, pyrtl.Const(max_value, bitwidth=width), incremented)


def multiply(a, b) -> pyrtl.WireVector:
    """Simple multiply wrapper using PyRTL's built-in multiplication."""

    a = _as_wire(a)
    b = _as_wire(b)
    return a * b
