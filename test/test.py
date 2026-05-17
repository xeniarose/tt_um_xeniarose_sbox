# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import struct
import os

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles

import numpy as np

SBOX = np.array([
    0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76,
    0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0,
    0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15,
    0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75,
    0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84,
    0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf,
    0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8,
    0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2,
    0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73,
    0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb,
    0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79,
    0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08,
    0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a,
    0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e,
    0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf,
    0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16,
], dtype='uint8')



IO_RWSEL = 0b0100_0000
IO_CLK = 0b1000_0000

MODE_READ = 1
MODE_WRITE = 2

class TestMeta:
    def __init__(self):
        self.mode = None
        self.io_dly = 1


async def io_write(dut, meta: TestMeta, addr: int, word: int) -> None:
    if meta.mode != MODE_WRITE:
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, meta.io_dly)
        meta.mode = MODE_WRITE
        assert (int(dut.uo_out.value) >> 1) & 1 == 0
        assert int(dut.uio_oe.value) == 0x00
        await ClockCycles(dut.clk, meta.io_dly)

    dut.uio_in.value = word & 0xFF
    dut.ui_in.value = IO_CLK | addr
    await ClockCycles(dut.clk, meta.io_dly)
    dut.uio_in.value = word & 0xFF
    dut.ui_in.value = addr
    await ClockCycles(dut.clk, meta.io_dly)


async def io_read(dut, meta: TestMeta, addr: int) -> int:
    if meta.mode != MODE_READ:
        dut.ui_in.value = IO_RWSEL
        await ClockCycles(dut.clk, meta.io_dly)
        meta.mode = MODE_READ
        assert (int(dut.uo_out.value) >> 1) & 1 == 1
        assert int(dut.uio_oe.value) == 0xff
        await ClockCycles(dut.clk, meta.io_dly)

    dut.ui_in.value = IO_CLK | IO_RWSEL | addr
    await ClockCycles(dut.clk, meta.io_dly)
    dut.ui_in.value = IO_RWSEL | addr
    await ClockCycles(dut.clk, meta.io_dly)
    word = (int(dut.uio_out.value) & 0xFF)

    return word


async def io_trigger(dut, meta: TestMeta, val=63) -> None:
    if meta.mode != MODE_WRITE:
        dut.ui_in.value = 0
        await ClockCycles(dut.clk, meta.io_dly)
        meta.mode = MODE_WRITE
        assert (int(dut.uo_out.value) >> 1) & 1 == 0
        assert int(dut.uio_oe.value) == 0x00
        await ClockCycles(dut.clk, meta.io_dly)

    dut.uio_in.value = 0
    dut.ui_in.value = IO_CLK | (val)
    await ClockCycles(dut.clk, meta.io_dly)
    dut.uio_in.value = 0
    dut.ui_in.value = (val)
    await ClockCycles(dut.clk, meta.io_dly)



async def test_init(dut):
    meta = TestMeta()

    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    return meta



@cocotb.test()
async def test_registers(dut):
    meta = await test_init(dut)
    dut._log.info("Test registers")

    for addr in range(0, 30):
        dut._log.info("Test register %s", addr)
        for val in [0x13, 0x12, 0x06, 0x21, 0x00, 0xff, 0x55, 0xaa, 0x99, 0x66]:
            await io_write(dut, meta, addr, val)
            rval = await io_read(dut, meta, addr)
            assert val == rval

@cocotb.test()
async def test_registers_long(dut):
    meta = await test_init(dut)
    meta.io_dly = 13
    dut._log.info("Test registers")

    for addr in range(0, 30):
        dut._log.info("Test register %s", addr)
        for val in [0x13, 0x12, 0x06, 0x21, 0x00, 0xff, 0x55, 0xaa, 0x99, 0x66]:
            await io_write(dut, meta, addr, val)
            rval = await io_read(dut, meta, addr)
            assert val == rval

@cocotb.test()
async def test_registers_verylong(dut):
    meta = await test_init(dut)
    meta.io_dly = 57
    dut._log.info("Test registers")

    for addr in range(0, 12):
        dut._log.info("Test register %s", addr)
        for val in [0x13, 0x12, 0x06, 0x21, 0x00, 0xff, 0x55, 0xaa, 0x99, 0x66]:
            await io_write(dut, meta, addr, val)
            rval = await io_read(dut, meta, addr)
            assert val == rval


@cocotb.test()
async def test_aes_sbox(dut):
    meta = await test_init(dut)
    dut._log.info("Test sbox")

    k0 = [227, 193, 69, 100, 12, 198, 78, 40, 193, 197, 29, 203, 98, 245, 252, 4, 237, 73, 62, 57, 3, 30, 69, 16, 181, 58, 209, 205, 161, 181, 7, 77]
    k1 = [183, 152, 86, 174, 90, 78, 137, 230, 103, 34, 103, 128, 198, 11, 225, 20, 245, 163, 123, 201, 15, 230, 211, 0, 43, 77, 170, 157, 73, 11, 84, 250]
    k2 = [28, 100, 213, 25, 118, 60, 251, 118, 216, 172, 245, 92, 22, 155, 151, 6, 232, 113, 39, 111, 120, 159, 30, 131, 45, 125, 18, 245, 66, 9, 222, 212]
    k3 = [97, 64, 42, 103, 118, 28, 169, 128, 252, 69, 145, 74, 43, 71, 168, 162, 147, 133, 186, 210, 144, 118, 48, 35, 192, 252, 67, 18, 116, 14, 28, 153]
    p0 = [108, 116, 175, 5, 131, 141, 165, 167, 192, 67, 143, 221, 47, 43, 171, 73, 73, 57, 251, 108, 158, 31, 206, 187, 23, 200, 116, 129, 233, 182, 64, 100]
    p1 = [29, 27, 187, 59, 122, 115, 126, 197, 182, 137, 208, 53, 184, 244, 104, 197, 79, 56, 215, 212, 117, 191, 215, 65, 31, 32, 63, 87, 253, 129, 201, 158]
    p2 = [55, 131, 249, 215, 14, 37, 31, 146, 179, 12, 96, 77, 170, 92, 201, 126, 175, 123, 52, 183, 221, 254, 161, 250, 27, 222, 42, 46, 53, 216, 143, 176]
    p3 = [43, 192, 125, 51, 139, 108, 116, 121, 57, 74, 112, 43, 91, 10, 251, 143, 29, 13, 164, 133, 210, 100, 225, 77, 41, 241, 189, 80, 47, 217, 75, 7]

    for a,b,c,d,e,f,g,h in zip(k0, k1, k2, k3, p0, p1, p2, p3):
        meta.io_dly = 1
        await io_write(dut, meta, 0, a)
        await io_write(dut, meta, 1, b)
        await io_write(dut, meta, 2, c)
        await io_write(dut, meta, 3, d)
        await io_write(dut, meta, 4, e)
        await io_write(dut, meta, 5, f)
        await io_write(dut, meta, 6, g)
        await io_write(dut, meta, 7, h)

        meta.io_dly = 43
        await io_trigger(dut, meta)
        meta.io_dly = 1

        assert (await io_read(dut, meta, 8)) == SBOX[a ^ e]
        assert (await io_read(dut, meta, 9)) == SBOX[b ^ f]
        assert (await io_read(dut, meta, 10)) == SBOX[c ^ g]
        assert (await io_read(dut, meta, 11)) == SBOX[d ^ h]


@cocotb.test()
async def test_aes_sbox2(dut):
    meta = await test_init(dut)
    dut._log.info("Test sbox")

    k0 = [227, 193, 69, 100, 12, 198, 78, 40, 193, 197, 29, 203, 98, 245, 252, 4, 237, 73, 62, 57, 3, 30, 69, 16, 181, 58, 209, 205, 161, 181, 7, 77]
    k1 = [183, 152, 86, 174, 90, 78, 137, 230, 103, 34, 103, 128, 198, 11, 225, 20, 245, 163, 123, 201, 15, 230, 211, 0, 43, 77, 170, 157, 73, 11, 84, 250]
    k2 = [28, 100, 213, 25, 118, 60, 251, 118, 216, 172, 245, 92, 22, 155, 151, 6, 232, 113, 39, 111, 120, 159, 30, 131, 45, 125, 18, 245, 66, 9, 222, 212]
    k3 = [97, 64, 42, 103, 118, 28, 169, 128, 252, 69, 145, 74, 43, 71, 168, 162, 147, 133, 186, 210, 144, 118, 48, 35, 192, 252, 67, 18, 116, 14, 28, 153]
    p0 = [108, 116, 175, 5, 131, 141, 165, 167, 192, 67, 143, 221, 47, 43, 171, 73, 73, 57, 251, 108, 158, 31, 206, 187, 23, 200, 116, 129, 233, 182, 64, 100]
    p1 = [29, 27, 187, 59, 122, 115, 126, 197, 182, 137, 208, 53, 184, 244, 104, 197, 79, 56, 215, 212, 117, 191, 215, 65, 31, 32, 63, 87, 253, 129, 201, 158]
    p2 = [55, 131, 249, 215, 14, 37, 31, 146, 179, 12, 96, 77, 170, 92, 201, 126, 175, 123, 52, 183, 221, 254, 161, 250, 27, 222, 42, 46, 53, 216, 143, 176]
    p3 = [43, 192, 125, 51, 139, 108, 116, 121, 57, 74, 112, 43, 91, 10, 251, 143, 29, 13, 164, 133, 210, 100, 225, 77, 41, 241, 189, 80, 47, 217, 75, 7]

    gates = os.environ.get("GATES", "?") == "yes"

    for a,b,c,d,e,f,g,h in zip(k0, k1, k2, k3, p0, p1, p2, p3):
        await io_write(dut, meta, 0, a)
        await io_write(dut, meta, 1, b)
        await io_write(dut, meta, 2, c)
        await io_write(dut, meta, 3, d)
        await io_write(dut, meta, 4, e)
        await io_write(dut, meta, 5, f)
        await io_write(dut, meta, 6, g)
        await io_write(dut, meta, 7, h)

        dut.uio_in.value = 0
        dut.ui_in.value = IO_CLK | 63
        await ClockCycles(dut.clk, 1)
        dut.uio_in.value = 0
        dut.ui_in.value = 63
        await ClockCycles(dut.clk, 3)

        if not gates:
            assert int(dut.user_project["\\register_file[8]"].value) == SBOX[a]
            assert int(dut.user_project["\\register_file[9]"].value) == SBOX[b]
            assert int(dut.user_project["\\register_file[10]"].value) == SBOX[c]
            assert int(dut.user_project["\\register_file[11]"].value) == SBOX[d]
        else:
            assert (
                (int(dut.user_project["\\register_file[8][0]"].value) << 0) |
                (int(dut.user_project["\\register_file[8][1]"].value) << 1) |
                (int(dut.user_project["\\register_file[8][2]"].value) << 2) |
                (int(dut.user_project["\\register_file[8][3]"].value) << 3) |
                (int(dut.user_project["\\register_file[8][4]"].value) << 4) |
                (int(dut.user_project["\\register_file[8][5]"].value) << 5) |
                (int(dut.user_project["\\register_file[8][6]"].value) << 6) |
                (int(dut.user_project["\\register_file[8][7]"].value) << 7)) == SBOX[a]
            assert (
                (int(dut.user_project["\\register_file[9][0]"].value) << 0) |
                (int(dut.user_project["\\register_file[9][1]"].value) << 1) |
                (int(dut.user_project["\\register_file[9][2]"].value) << 2) |
                (int(dut.user_project["\\register_file[9][3]"].value) << 3) |
                (int(dut.user_project["\\register_file[9][4]"].value) << 4) |
                (int(dut.user_project["\\register_file[9][5]"].value) << 5) |
                (int(dut.user_project["\\register_file[9][6]"].value) << 6) |
                (int(dut.user_project["\\register_file[9][7]"].value) << 7)) == SBOX[b]
            assert (
                (int(dut.user_project["\\register_file[10][0]"].value) << 0) |
                (int(dut.user_project["\\register_file[10][1]"].value) << 1) |
                (int(dut.user_project["\\register_file[10][2]"].value) << 2) |
                (int(dut.user_project["\\register_file[10][3]"].value) << 3) |
                (int(dut.user_project["\\register_file[10][4]"].value) << 4) |
                (int(dut.user_project["\\register_file[10][5]"].value) << 5) |
                (int(dut.user_project["\\register_file[10][6]"].value) << 6) |
                (int(dut.user_project["\\register_file[10][7]"].value) << 7)) == SBOX[c]
            assert (
                (int(dut.user_project["\\register_file[11][0]"].value) << 0) |
                (int(dut.user_project["\\register_file[11][1]"].value) << 1) |
                (int(dut.user_project["\\register_file[11][2]"].value) << 2) |
                (int(dut.user_project["\\register_file[11][3]"].value) << 3) |
                (int(dut.user_project["\\register_file[11][4]"].value) << 4) |
                (int(dut.user_project["\\register_file[11][5]"].value) << 5) |
                (int(dut.user_project["\\register_file[11][6]"].value) << 6) |
                (int(dut.user_project["\\register_file[11][7]"].value) << 7)) == SBOX[d]

        await ClockCycles(dut.clk, 1)

        if not gates:
            assert int(dut.user_project["\\register_file[8]"].value) == SBOX[a ^ e]
            assert int(dut.user_project["\\register_file[9]"].value) == SBOX[b ^ f]
            assert int(dut.user_project["\\register_file[10]"].value) == SBOX[c ^ g]
            assert int(dut.user_project["\\register_file[11]"].value) == SBOX[d ^ h]
        else:
            assert (
                (int(dut.user_project["\\register_file[8][0]"].value) << 0) |
                (int(dut.user_project["\\register_file[8][1]"].value) << 1) |
                (int(dut.user_project["\\register_file[8][2]"].value) << 2) |
                (int(dut.user_project["\\register_file[8][3]"].value) << 3) |
                (int(dut.user_project["\\register_file[8][4]"].value) << 4) |
                (int(dut.user_project["\\register_file[8][5]"].value) << 5) |
                (int(dut.user_project["\\register_file[8][6]"].value) << 6) |
                (int(dut.user_project["\\register_file[8][7]"].value) << 7)) == SBOX[a ^ e]
            assert (
                (int(dut.user_project["\\register_file[9][0]"].value) << 0) |
                (int(dut.user_project["\\register_file[9][1]"].value) << 1) |
                (int(dut.user_project["\\register_file[9][2]"].value) << 2) |
                (int(dut.user_project["\\register_file[9][3]"].value) << 3) |
                (int(dut.user_project["\\register_file[9][4]"].value) << 4) |
                (int(dut.user_project["\\register_file[9][5]"].value) << 5) |
                (int(dut.user_project["\\register_file[9][6]"].value) << 6) |
                (int(dut.user_project["\\register_file[9][7]"].value) << 7)) == SBOX[b ^ f]
            assert (
                (int(dut.user_project["\\register_file[10][0]"].value) << 0) |
                (int(dut.user_project["\\register_file[10][1]"].value) << 1) |
                (int(dut.user_project["\\register_file[10][2]"].value) << 2) |
                (int(dut.user_project["\\register_file[10][3]"].value) << 3) |
                (int(dut.user_project["\\register_file[10][4]"].value) << 4) |
                (int(dut.user_project["\\register_file[10][5]"].value) << 5) |
                (int(dut.user_project["\\register_file[10][6]"].value) << 6) |
                (int(dut.user_project["\\register_file[10][7]"].value) << 7)) == SBOX[c ^ g]
            assert (
                (int(dut.user_project["\\register_file[11][0]"].value) << 0) |
                (int(dut.user_project["\\register_file[11][1]"].value) << 1) |
                (int(dut.user_project["\\register_file[11][2]"].value) << 2) |
                (int(dut.user_project["\\register_file[11][3]"].value) << 3) |
                (int(dut.user_project["\\register_file[11][4]"].value) << 4) |
                (int(dut.user_project["\\register_file[11][5]"].value) << 5) |
                (int(dut.user_project["\\register_file[11][6]"].value) << 6) |
                (int(dut.user_project["\\register_file[11][7]"].value) << 7)) == SBOX[d ^ h]

        await ClockCycles(dut.clk, 10)

        assert (await io_read(dut, meta, 8)) == SBOX[a ^ e]
        assert (await io_read(dut, meta, 9)) == SBOX[b ^ f]
        assert (await io_read(dut, meta, 10)) == SBOX[c ^ g]
        assert (await io_read(dut, meta, 11)) == SBOX[d ^ h]


@cocotb.test()
async def test_present(dut):
    meta = await test_init(dut)
    dut._log.info("Test present")

    vecs = [
        (0x0000000000000000, 0x00000000000000000000, 0x5579C1387B228445),
        (0x0000000000000000, 0xFFFFFFFFFFFFFFFFFFFF, 0xE72C46C0F5945049),
        (0xFFFFFFFFFFFFFFFF, 0x00000000000000000000, 0xA112FFC72F68417B),
        (0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFFFFFF, 0x3333DCD3213210D2),
    ]

    for (pt, key, ct) in vecs:
        for i in range(12, 22):
            await io_write(dut, meta, i, (key >> ((i-12)*8)&0xFF))

        for i in range(22, 30):
            await io_write(dut, meta, i, (pt >> ((i-22)*8)&0xFF))

        await io_trigger(dut, meta, 62)

        await ClockCycles(dut.clk, 32)

        ct_chk = 0
        for i in range(30, 38):
            ct_chk |= (await io_read(dut, meta, i)) << ((i-30)*8)

        print(hex(key), hex(pt), hex(ct), hex(ct_chk))
        assert ct_chk == ct
