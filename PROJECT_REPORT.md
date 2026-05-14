# Improved Hardware Library in PyRTL

## Introduction

I built this project to learn how reusable hardware blocks can be written in
PyRTL.  The result is a small hardware library with primitives, arithmetic
blocks, memory blocks, and simple valid/ready dataflow blocks.

This is not a complete Intel primitive library.  It is a freshman research
project focused on clear code, simulation, and testing.

The project started from a simple question: if many hardware designs use the
same kinds of parts, can I build a small library of those parts myself?  I used
that question to practice both digital design and Python-based hardware
simulation.

## Background

PyRTL lets hardware be described in Python at the register-transfer level.  I
used it because I could build circuits and simulate them quickly while still
thinking about real hardware ideas like wires, registers, memories, and
combinational logic.

I looked at FPGA-style primitive libraries because they collect common blocks
in one place.  I also looked at compositional dataflow ideas because
valid/ready handshaking is a common way to connect pipeline stages.

I did not try to copy a professional library.  Instead, I used those projects
as motivation for what kinds of blocks are worth learning about.

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

This staged approach helped because each part built on something earlier.  For
example, the FIFO used registers and mux-style selection.  The dataflow buffer
used registers too, but added the idea of waiting for a downstream ready
signal.

## Implemented Components

The primitive module includes register helpers, counters, muxes, demuxes, a
decoder, a priority encoder, and a shifter.

These were the first blocks I worked on because they are common in many
circuits.  They also helped me get used to PyRTL wires, bitwidths, and
simulation.

The arithmetic module includes half adders, full adders, a ripple-carry adder,
a subtractor, equality and comparison logic, a saturating incrementer, and a
multiply wrapper.

The ripple-carry adder was one of the most useful learning pieces.  It starts
with one-bit adders and connects them together, which made the structure of the
circuit easier to understand.

The memory module includes a ROM wrapper, synchronous RAM wrapper, small FIFO,
and circular buffer wrapper.  The FIFO uses registers plus head, tail, and
count registers.

The FIFO was important because it showed me that sequential circuits need more
careful thinking than simple combinational logic.  The output depends not just
on the inputs, but also on what happened in previous cycles.

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

This was not meant to be a full dataflow system.  I mainly wanted to understand
the basic pattern and see how it could be written in PyRTL.

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

I also ran extra manual stress checks while developing.  Those checks helped me
test more input combinations for arithmetic, FIFO behavior, memory reads, and
dataflow handshakes.

## Results

The project works as a small educational PyRTL library.  It has code, tests,
examples, and documentation.  The examples show basic selection logic,
counters, adders, FIFOs, and small dataflow systems.

The library is not tuned for speed or area, but it is understandable and
testable.

The most important result is that each major block can be simulated and tested
on its own.  That makes the project easier to explain and easier to extend.

## Challenges

The FIFO was one of the harder parts because the head pointer, tail pointer,
count, full flag, and empty flag all have to agree.

The dataflow section was also challenging because `ready` moves backward
through the circuit while `data` and `valid` move forward.  That was confusing
at first, but the tests made it easier to see what was happening.

Another challenge was keeping the project at the right level.  I wanted it to
be serious, but I did not want to pretend it was a professional FPGA library.
That is why the final version keeps the code direct and the limitations clear.

## Lessons Learned

I learned that a small hardware block still needs a clear interface.  I also
learned that tests are useful even when the circuit looks simple.

The biggest lesson was that reusable hardware is not just about writing a
function.  It also needs examples, tests, and honest limits.

I also learned that simulation is a good way to build confidence.  Even when I
thought a block was correct, writing a test forced me to be more exact about
what the block should do.

## Future Work

Future work could include signed arithmetic, more RAM tests, waveform output,
Verilog generation examples, and a larger streaming pipeline demo.

## Conclusion

This project helped me learn PyRTL and basic hardware library design.  It is
not ready for real hardware projects, but it is a complete learning project
with reusable blocks, tests, examples, and a simple dataflow exploration.
