# Improved Hardware Library in PyRTL

## Introduction

I built this project to learn how reusable hardware blocks can be written in
PyRTL.  The result is a small hardware library with primitives, arithmetic
blocks, memory blocks, and simple valid/ready dataflow blocks.

This is not a complete Intel primitive library.  It is a freshman research
project focused on clear code, simulation, and testing.

## Background

PyRTL lets hardware be described in Python at the register-transfer level.  I
used it because I could build circuits and simulate them quickly while still
thinking about real hardware ideas like wires, registers, memories, and
combinational logic.

I looked at FPGA-style primitive libraries because they collect common blocks
in one place.  I also looked at compositional dataflow ideas because
valid/ready handshaking is a common way to connect pipeline stages.

## Project Goals

My goals were:

- make a small reusable PyRTL library
- keep the code understandable for a beginner
- include primitives, arithmetic, memory, and dataflow components
- write tests for the most important behavior
- make examples that show how to use the blocks
- be honest about what the project does not do

## Design Approach

I split the project into four files:

- `primitives.py` for basic building blocks
- `arithmetic.py` for adders and comparators
- `memory.py` for ROM, RAM, FIFO, and circular buffer ideas
- `dataflow.py` for valid/ready experiments

I tried to keep the functions small.  Most of them return PyRTL wires.  When a
block has several outputs, such as the FIFO, I grouped the outputs together so
they are easier to use.

The project grew in stages over the year.  I started with simple muxes and
registers, then added arithmetic, then memory, then dataflow circuits.

## Implemented Components

The primitive module includes register helpers, counters, muxes, demuxes, a
decoder, a priority encoder, and a shifter.

The arithmetic module includes half adders, full adders, a ripple-carry adder,
a subtractor, equality and comparison logic, a saturating incrementer, and a
multiply wrapper.

The memory module includes a ROM wrapper, synchronous RAM wrapper, small FIFO,
and circular buffer wrapper.  The FIFO uses registers plus head, tail, and
count registers.

## Dataflow Circuit Exploration

The dataflow module uses a small `DataflowSignal` class with:

- `data`
- `valid`
- `ready`

I implemented a one-entry buffer, pass-through stage, all-or-nothing fork, mux,
demux, unit-rate actor, and priority merge.  The main idea is that data
transfers only when `valid` and `ready` are both high.

This part helped me understand backpressure.  For example, a fork should only
accept input when both outputs are ready.

## Testing

I used pytest and PyRTL simulation.  Each test builds a small circuit, runs
simulation steps, and checks the output.

The tests cover:

- mux and demux behavior
- n-bit and up/down counters
- ripple-carry adder correctness
- comparators
- FIFO behavior
- valid/ready pipeline behavior
- fork behavior
- dataflow mux/demux behavior
- priority merge behavior

## Results

The project works as a small educational PyRTL library.  It has code, tests,
examples, and documentation.  The examples show basic selection logic,
counters, adders, FIFOs, and small dataflow systems.

The library is not tuned for speed or area, but it is understandable and
testable.

## Challenges

The FIFO was one of the harder parts because the head pointer, tail pointer,
count, full flag, and empty flag all have to agree.

The dataflow section was also challenging because `ready` moves backward
through the circuit while `data` and `valid` move forward.  That was confusing
at first, but the tests made it easier to see what was happening.

## Lessons Learned

I learned that a small hardware block still needs a clear interface.  I also
learned that tests are useful even when the circuit looks simple.

The biggest lesson was that reusable hardware is not just about writing a
function.  It also needs examples, tests, and honest limits.

## Future Work

Future work could include signed arithmetic, more RAM tests, waveform output,
Verilog generation examples, and a larger streaming pipeline demo.

## Conclusion

This project helped me learn PyRTL and basic hardware library design.  It is
not ready for real hardware projects, but it is a complete learning project
with reusable blocks, tests, examples, and a simple dataflow exploration.
