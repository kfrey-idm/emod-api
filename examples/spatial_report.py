#!/usr/bin/env python3

from collections import namedtuple
import numpy as np
import os
from argparse import ArgumentParser
from emod_api.spatialreports.spatial import SpatialReport

MATPLOTLIB = True
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    print("This example requires the matplotlib package.")
    MATPLOTLIB = False

SCRIPT_PATH = os.path.realpath(__file__)
WORKING_DIRECTORY = os.path.dirname(SCRIPT_PATH)

Coordinate = namedtuple("Coordinate", ["x", "y"])


def decode(node_id: int):

    x = node_id >> 16
    y = (node_id % 65536) - 1

    return Coordinate(x, y)


def main(filename: str):

    report = SpatialReport(filename)

    plt.xkcd()

    # Show prevalence over time for first node
    plt.subplots(num=os.path.basename(filename))
    plt.plot(report.nodes[report.node_ids[0]].data)
    plt.title(f"Prevalence for Node {report.node_ids[0]}")
    plt.xlabel("Time Step")
    plt.ylabel("Prevalence")
    plt.show()

    # Show prevalence at time step 180
    coordinates = list(map(decode, report.node_ids))
    min_x = min(map(lambda c: c.x, coordinates))
    max_x = max(map(lambda c: c.x, coordinates))
    min_y = min(map(lambda c: c.y, coordinates))
    max_y = max(map(lambda c: c.y, coordinates))

    width = max_x - min_x + 1
    height = max_y - min_y + 1
    garki = np.zeros((height, width), dtype=np.float32)
    time_step = min(report.time_steps-1, 180)
    for node_id in report.node_ids:
        x, y = decode(node_id)
        garki[y - min_y, x - min_x] = report.nodes[node_id][time_step]

    plt.subplots(num=os.path.basename(filename))
    plt.imshow(garki, origin="lower", cmap="RdYlGn_r")
    plt.title(f"Prevalence at Time Step {time_step}")
    plt.xlabel("East-West")
    plt.ylabel("South-North")
    plt.show()

    return


def dump_source():

    with open(SCRIPT_PATH, "r") as file:
        print(file.read())

    return


if __name__ == "__main__":
    parser = ArgumentParser()
    default_filename = os.path.join(
        WORKING_DIRECTORY,
        "..",
        "tests",
        "data",
        "spatialreports",
        "SpatialReport_Prevalence.bin",
    )
    parser.add_argument(
        "-f", "--filename", default=default_filename, help="spatial report filename"
    )
    parser.add_argument(
        "-g",
        "--get",
        default=False,
        action="store_true",
        help="Write source code for this example to stdout.",
    )

    args = parser.parse_args()

    if args.get:
        dump_source()
    elif MATPLOTLIB:
        main(args.filename)
