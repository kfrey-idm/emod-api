#!/usr/bin/env python3

import numpy as np
import os
from argparse import ArgumentParser
from collections import namedtuple
from emod_api.weather.weather import Weather, Metadata, WeatherNode

MATPLOTLIB = True
try:
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize
except ModuleNotFoundError:
    print("This example requires the matplotlib package.")
    MATPLOTLIB = False

SCRIPT_PATH = os.path.realpath(__file__)
WORKING_DIRECTORY = os.path.dirname(SCRIPT_PATH)


def main(filename: str, day: int, minimum, maximum, cmap: str):

    weather = Weather(filename)

    plt.xkcd()

    node_id = weather.node_ids[0]
    plt.subplots(num=os.path.basename(filename))
    plt.plot(weather.nodes[node_id].data)
    plt.title(f"Values for Node {node_id}")
    plt.xlabel("Time Step")
    plt.ylabel("Value")
    plt.show()

    Coordinate = namedtuple("Coordinate", ["x", "y"])

    def decode(nid):
        """Decode node IDs into x and y coordinates (indices)."""
        x_index = nid >> 16
        y_index = (nid % 65536) - 1

        return Coordinate(x_index, y_index)

    coordinates = list(map(decode, weather.node_ids))
    min_x = min(map(lambda c: c.x, coordinates))
    max_x = max(map(lambda c: c.x, coordinates))
    min_y = min(map(lambda c: c.y, coordinates))
    max_y = max(map(lambda c: c.y, coordinates))

    width = max_x - min_x + 1
    height = max_y - min_y + 1
    grid = np.zeros((height, width), dtype=np.float32)
    for node_id in weather.node_ids:
        x, y = decode(node_id)
        grid[y - min_y, x - min_x] = weather.nodes[node_id][day]

    plt.subplots(num=os.path.basename(filename))
    plt.imshow(grid, origin="lower", cmap=cmap, norm=Normalize(minimum, maximum))
    plt.title(f"Values at Time Step {day}")
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
    default_file = os.path.join(
        WORKING_DIRECTORY,
        "..",
        "tests",
        "data",
        "weatherfiles",
        "Kenya_Nairobi_2.5arcmin_air_temperature_daily.bin",
    )
    parser.add_argument(
        "-f", "--filename", type=str, default=default_file, help="Climate file name"
    )
    parser.add_argument(
        "-d", "--day", type=int, default=180, help="Day of year to display, default=180"
    )
    parser.add_argument(
        "-m",
        "--map",
        type=str,
        default="RdYlBu_r",
        help="Matplotlib colormap for image",
    )
    parser.add_argument(
        "-n", "--min", type=float, default=0.0, help="Minimum value for scaling"
    )
    # https://en.wikipedia.org/wiki/List_of_weather_records#Highest_temperatures_ever_recorded
    parser.add_argument(
        "-x", "--max", type=float, default=60.0, help="Maximum value for scaling"
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
        main(args.filename, args.day, args.min, args.max, args.map)
