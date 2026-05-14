import pyrtl

from src.memory import circular_buffer, rom_read, small_fifo, synchronous_ram


def output_of(wire, name):
    out = pyrtl.Output(len(wire), name)
    out <<= wire
    return out


def test_fifo_behavior():
    pyrtl.reset_working_block()
    data_in = pyrtl.Input(8, "data_in")
    enqueue = pyrtl.Input(1, "enqueue")
    dequeue = pyrtl.Input(1, "dequeue")
    fifo = small_fifo(data_in, enqueue, dequeue, width=8, depth=4)
    output_of(fifo.data_out, "data_out")
    output_of(fifo.empty, "empty")
    output_of(fifo.full, "full")
    output_of(fifo.count, "count")

    sim = pyrtl.Simulation()

    sim.step({"data_in": 10, "enqueue": 1, "dequeue": 0})
    assert sim.inspect("empty") == 1
    assert sim.inspect("count") == 0

    sim.step({"data_in": 20, "enqueue": 1, "dequeue": 0})
    assert sim.inspect("data_out") == 10
    assert sim.inspect("empty") == 0
    assert sim.inspect("count") == 1

    sim.step({"data_in": 0, "enqueue": 0, "dequeue": 1})
    assert sim.inspect("data_out") == 10
    assert sim.inspect("count") == 2

    sim.step({"data_in": 0, "enqueue": 0, "dequeue": 0})
    assert sim.inspect("data_out") == 20
    assert sim.inspect("count") == 1


def test_fifo_full_flag():
    pyrtl.reset_working_block()
    data_in = pyrtl.Input(4, "data_in")
    enqueue = pyrtl.Input(1, "enqueue")
    dequeue = pyrtl.Input(1, "dequeue")
    fifo = small_fifo(data_in, enqueue, dequeue, width=4, depth=2)
    output_of(fifo.full, "full")
    output_of(fifo.count, "count")

    sim = pyrtl.Simulation()
    sim.step({"data_in": 1, "enqueue": 1, "dequeue": 0})
    sim.step({"data_in": 2, "enqueue": 1, "dequeue": 0})
    sim.step({"data_in": 3, "enqueue": 1, "dequeue": 0})
    assert sim.inspect("full") == 1
    assert sim.inspect("count") == 2


def test_rom_wrapper():
    pyrtl.reset_working_block()
    address = pyrtl.Input(2, "address")
    table = {0: 3, 1: 5, 2: 8, 3: 13}
    output_of(rom_read(table, address, bitwidth=4), "data")

    sim = pyrtl.Simulation()
    for address_value, expected in table.items():
        sim.step({"address": address_value})
        assert sim.inspect("data") == expected


def test_synchronous_ram_wrapper_readback():
    pyrtl.reset_working_block()
    read_address = pyrtl.Input(2, "read_address")
    write_address = pyrtl.Input(2, "write_address")
    write_data = pyrtl.Input(8, "write_data")
    write_enable = pyrtl.Input(1, "write_enable")
    read_data, _mem = synchronous_ram(
        read_address,
        write_address,
        write_data,
        write_enable,
        bitwidth=8,
        addrwidth=2,
    )
    output_of(read_data, "read_data")

    sim = pyrtl.Simulation()
    values = [11, 22, 33, 44]
    for address, value in enumerate(values):
        sim.step(
            {
                "read_address": 0,
                "write_address": address,
                "write_data": value,
                "write_enable": 1,
            }
        )

    for address, expected in enumerate(values):
        sim.step(
            {
                "read_address": address,
                "write_address": 0,
                "write_data": 0,
                "write_enable": 0,
            }
        )
        sim.step(
            {
                "read_address": address,
                "write_address": 0,
                "write_data": 0,
                "write_enable": 0,
            }
        )
        assert sim.inspect("read_data") == expected


def test_circular_buffer_wrapper_smoke():
    pyrtl.reset_working_block()
    data_in = pyrtl.Input(4, "data_in")
    write = pyrtl.Input(1, "write")
    read = pyrtl.Input(1, "read")
    cbuf = circular_buffer(data_in, write, read, width=4, depth=3)
    output_of(cbuf.data_out, "data_out")
    output_of(cbuf.count, "count")

    sim = pyrtl.Simulation()
    sim.step({"data_in": 6, "write": 1, "read": 0})
    sim.step({"data_in": 7, "write": 1, "read": 0})
    assert sim.inspect("data_out") == 6
    assert sim.inspect("count") == 1
