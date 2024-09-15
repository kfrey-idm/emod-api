#!/usr/bin/python

from __future__ import print_function
import argparse
import emod_api.serialization.dtkFileTools as dft
import os
import random

try:
    import snappy
    SNAPPY_SUPPORT = True
except:
    SNAPPY_SUPPORT = False

SCRIPT_PATH = os.path.realpath(__file__)
WORKING_DIRECTORY = os.path.dirname(SCRIPT_PATH)


def source(filename):
    return os.path.join(WORKING_DIRECTORY, "data", "serialization", filename)


def dest(filename):
    return os.path.join(WORKING_DIRECTORY, "data", "serialization", filename)


def main(arguments):

    # put this and make_snappy first since other calls depend on these files
    if arguments.make_uncompressed:
        make_uncompressed()

    if SNAPPY_SUPPORT:

        if arguments.make_snappy:
            make_snappy()

        if arguments.make_bad_chunk_snappy:
            make_bad_chunk_snappy()

        if arguments.make_bad_sim_snappy:
            make_bad_sim_snappy()

        if arguments.make_lz4_snappy:
            make_lz4_snappy()

        if arguments.make_none_snappy:
            make_none_snappy()

    else:
        print("** NOTE ** [python-]snappy not installed, snappy [de]compression support not available.")

    if arguments.make_bad_chunk_lz4:
        make_bad_chunk_lz4()

    if arguments.make_bad_sim_lz4:
        make_bad_sim_lz4()

    if arguments.make_lz4_none:
        make_lz4_none()

    if arguments.make_none_lz4:
        make_none_lz4()

    if arguments.make_snappy_lz4:
        make_snappy_lz4()

    if arguments.make_snappy_none:
        make_snappy_none()

    return


def make_bad_chunk_lz4():

    dtk = dft.read(source("baseline.dtk"))
    # get the chunk, first node, not simulation
    chunk = dtk.chunks[1]
    # choose an index
    index = random.randint(0, len(chunk))

    # convert string to array of chars
    chunk = [c for c in chunk]
    # perturb the bits
    old = chunk[index]
    new = chr(~ord(old) % 256)
    chunk[index] = new
    # convert array of chars back to string
    chunk = "".join(chunk)

    dtk.chunks[1] = chunk

    print(
        "Flipped bits of chunk #1 byte {0} ({1} -> {2})".format(
            index, ord(old), ord(new)
        )
    )

    dft.write(dtk, dest("bad-chunk-lz4.dtk"))

    return


def make_bad_chunk_snappy():

    dtk = dft.read(source("snappy.dtk"))
    # get the chunk, first node, not simulation
    chunk = dtk.chunks[1]
    # choose an index
    index = random.randint(0, len(chunk))

    # convert string to array of chars
    chunk = [c for c in chunk]
    # perturb the bits
    old = chunk[index]
    new = chr(~ord(old) % 256)
    chunk[index] = new
    # convert array of chars back to string
    chunk = "".join(chunk)

    dtk.chunks[1] = chunk

    print(
        "Flipped bits of chunk #1 byte {0} ({1} -> {2})".format(
            index, ord(old), ord(new)
        )
    )

    dft.write(dtk, dest("bad-chunk-snappy.dtk"))

    return


def make_bad_sim_lz4():

    dtk = dft.read(source("baseline.dtk"))
    sim_text = dtk.contents[0]
    sim_text = sim_text.replace(
        '"__class__":"Simulation"', '"__class__"*"Simulation"', 1
    )
    dtk.contents[0] = sim_text
    dft.write(dtk, dest("bad-sim-lz4.dtk"))

    return


def make_bad_sim_snappy():

    dtk = dft.read(source("snappy.dtk"))
    sim_text = dtk.contents[0]
    sim_text = sim_text.replace(
        '"__class__":"Simulation"', '"__class__"*"Simulation"', 1
    )
    dtk.contents[0] = sim_text
    dft.write(dtk, dest("bad-sim-snappy.dtk"))

    return


def make_lz4_none():

    dtk = dft.read(source("uncompressed.dtk"))
    dtk.header["compressed"] = True
    dtk.header["engine"] = dft.LZ4
    dft.write(dtk, dest("lz4-none.dtk"))

    return


def make_lz4_snappy():

    dtk = dft.read(source("snappy.dtk"))
    dtk.header["compressed"] = True
    dtk.header["engine"] = dft.LZ4
    dft.write(dtk, dest("lz4-snappy.dtk"))

    return


def make_none_lz4():

    dtk = dft.read(source("baseline.dtk"))
    dtk.header["compressed"] = False
    dtk.header["engine"] = dft.NONE
    dft.write(dtk, dest("none-lz4.dtk"))

    return


def make_none_snappy():

    dtk = dft.read(source("snappy.dtk"))
    dtk.header["compressed"] = False
    dtk.header["engine"] = dft.NONE
    dft.write(dtk, dest("none-snappy.dtk"))

    return


def make_snappy_lz4():

    dtk = dft.read(source("baseline.dtk"))
    dtk.header["compressed"] = True
    dtk.header["engine"] = dft.SNAPPY
    dft.write(dtk, dest("serialization", "snappy-lz4.dtk"))

    return


def make_snappy_none():

    dtk = dft.read(source("uncompressed.dtk"))
    dtk.header["compressed"] = True
    dtk.header["engine"] = dft.SNAPPY
    dft.write(dtk, dest("snappy-none.dtk"))

    return


def make_uncompressed():

    dtk = dft.read(source("baseline.dtk"))
    dtk.compression = dft.NONE
    dft.write(dtk, dest("uncompressed.dtk"))

    return


def make_snappy():

    dtk = dft.read(source("baseline.dtk"))
    dtk.compression = dft.SNAPPY
    dft.write(dtk, dest("snappy.dtk"))

    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--make-bad-chunk-lz4", default=False, action="store_true")
    parser.add_argument("--make-bad-chunk-snappy", default=False, action="store_true")
    parser.add_argument("--make-bad-sim-lz4", default=False, action="store_true")
    parser.add_argument("--make-bad-sim-snappy", default=False, action="store_true")
    parser.add_argument("--make-lz4-none", default=False, action="store_true")
    parser.add_argument("--make-lz4-snappy", default=False, action="store_true")
    parser.add_argument("--make-none-lz4", default=False, action="store_true")
    parser.add_argument("--make-none-snappy", default=False, action="store_true")
    parser.add_argument("--make-snappy-lz4", default=False, action="store_true")
    parser.add_argument("--make-snappy-none", default=False, action="store_true")
    parser.add_argument("--make-uncompressed", default=False, action="store_true")
    parser.add_argument("--make-snappy", default=False, action="store_true")

    args = parser.parse_args()

    main(args)
