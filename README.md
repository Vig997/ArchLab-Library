# Improved Hardware Library in PyRTL

This is a year-long research project about building small reusable
hardware blocks in PyRTL.  I wanted it to feel like a tiny, beginner-friendly
version of an FPGA primitive library.

The project is not a real Intel library replacement.  It is a learning project
focused on simulation, clear code, and tests.

The main idea is to take hardware blocks that show up again and again in class
or lab work and put them into one small Python library.  Some blocks are very
basic, like muxes and counters.  Others are a little more involved, like a
FIFO queue and valid/ready pipeline pieces.  I built the project this way
because I wanted to move from individual circuits toward thinking about how
circuits can be organized and reused.

## Project Overview

I built four small groups of components:

- `src/primitives.py`: registers, counters, muxes, demuxes, decoder, priority
  encoder, and shifter
- `src/arithmetic.py`: adders, subtractor, comparators, saturating increment,
  and multiply wrapper
- `src/memory.py`: ROM helper, synchronous RAM helper, FIFO, and circular
  buffer wrapper
- `src/dataflow.py`: simple valid/ready channels, buffers, all-or-nothing fork,
  mux, demux, unit-rate actor, and priority merge

There are also pytest tests and runnable examples in `tests/` and `examples/`.

The examples are meant to be small enough to read in one sitting.  Each one
builds a PyRTL circuit, runs a short simulation, and prints the output.  The
tests are more complete and check the behavior across more input cases.

## Motivation

I made this project because I kept seeing the same hardware blocks in digital
design: muxes, counters, adders, registers, memories, and FIFOs.  I wanted to
understand how those blocks can be written in Python using PyRTL.

I also wanted to try valid/ready dataflow circuits.  The idea is simple: data
moves when `valid` and `ready` are both high.  That made buffers and pipelines
more interesting to study.

At the start, I mostly thought of hardware as one circuit at a time.  By the
end, I was thinking more about interfaces: what inputs a block needs, what
outputs it produces, and how another block would connect to it.  That was one
of the biggest reasons for making this a library instead of just a collection
of unrelated demos.

## What PyRTL Is

PyRTL is a Python library for describing hardware at the register-transfer
level.  Instead of writing every circuit directly in Verilog, I can build wires,
registers, memories, and logic with Python and then simulate the circuit.

## Why Reusable Blocks Matter

Reusable blocks make bigger circuits easier to build.  If a counter or FIFO has
already been tested, I can use it in another design without starting over.
Named blocks also make the circuit easier to read.

## Inspiration

The project is loosely inspired by Intel-style FPGA primitive libraries and by
ROHD-HCL.  I only used those projects as ideas.  This library is much smaller
and is meant for learning.

The dataflow part is inspired by compositional dataflow circuits, but I only
implemented the basic valid/ready idea.

## What Was Implemented

Main blocks included:

- register helpers: normal, enabled, and resettable registers
- counters: n-bit counter and up/down counter
- selection logic: `mux2`, `mux4`, `demux2`, `demux4`, decoder, priority
  encoder
- arithmetic: half adder, full adder, ripple-carry adder, subtractor,
  comparators, saturating incrementer, multiply wrapper
- memory: ROM, synchronous RAM, FIFO, circular buffer wrapper
- dataflow: channel helper, buffer, pass-through stage, all-or-nothing fork,
  mux, demux, unit-rate actor, priority merge

The arithmetic section includes both small one-bit blocks and wider blocks.
The ripple-carry adder is useful because it shows how a larger circuit can be
built by connecting repeated smaller pieces.

The memory section is mostly for learning how state works.  The FIFO is not
the most efficient design, but it clearly shows the head pointer, tail pointer,
count, empty flag, and full flag.

The dataflow section is the newest part of the project.  It is there to show
how simple pipeline stages can pause when the next stage is not ready.

## What Was Not Implemented

- a full Intel primitive library
- real FPGA timing models
- special FPGA blocks like DSPs or PLLs
- a full dataflow compiler
- a polished package ready to publish

## Install

```bash
pip install -r requirements.txt
```

## Run Tests

```bash
pytest
```

The tests check muxes, demuxes, counters, arithmetic, FIFO behavior, and the
valid/ready dataflow blocks.

I used tests because hardware bugs can be hard to see just by looking at the
code.  Running the same circuit over many input values helped me catch mistakes
and made the project feel more reliable.

## Run Examples

```bash
python examples/01_basic_mux_demo.py
python examples/02_counter_demo.py
python examples/03_adder_demo.py
python examples/04_fifo_demo.py
python examples/05_dataflow_pipeline_demo.py
python examples/06_fork_mux_demux_demo.py
python examples/07_small_streaming_system_demo.py
```

## Simple Demo Plan

If I was presenting this project, I would show it in this order:

1. Run `python examples/01_basic_mux_demo.py` to show a basic hardware block.
2. Run `python examples/03_adder_demo.py` to show the ripple-carry adder.
3. Run `python examples/04_fifo_demo.py` to show a sequential memory block.
4. Run `python examples/05_dataflow_pipeline_demo.py` to show valid/ready.
5. Run `pytest` to show that the components are tested.

## What I Learned

I learned that small hardware blocks still have important details.  Counters
need clear enable behavior.  FIFOs need correct head, tail, count, full, and
empty logic.  Valid/ready circuits need careful backpressure connections.

I also learned that examples and tests matter just as much as the code.

The project also helped me get more comfortable reading PyRTL simulation
results.  A lot of the learning came from writing a circuit, guessing what the
next cycle should do, and then checking whether the simulation matched that.

## Year-Long Progress

- First: basic PyRTL syntax, muxes, demuxes, and registers
- Then: counters, adders, comparators, and more tests
- Later: FIFO logic and simple memory wrappers
- Last: valid/ready dataflow blocks, examples, cleanup, and this report

## Limitations

This project is still small.  The FIFO is register-based and not tuned for a
real FPGA.  The dataflow blocks are useful for learning but do not cover all
the rules from research papers.  I cared more about making the behavior right
and understandable than about timing, area, or speed.

## Future Work

- add signed arithmetic blocks
- add waveform examples
- add a small ALU example
- add more RAM tests
- generate Verilog for a few blocks
- build a larger streaming demo
