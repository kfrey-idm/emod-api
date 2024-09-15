#!/usr/bin/env python3

import os
from argparse import ArgumentParser
from emod_api.channelreports.channels import ChannelReport

MATPLOTLIB = True
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    print("This example requires the matplotlib package.")
    MATPLOTLIB = False

PANDAS = True
try:
    import pandas as pd
except ModuleNotFoundError:
    print("This example requires the pandas package.")
    PANDAS = False

SCRIPT_PATH = os.path.realpath(__file__)
WORKING_DIRECTORY = os.path.dirname(SCRIPT_PATH)


def main(filename: str):

    icj = ChannelReport(filename)

    plt.xkcd()

    plt.subplots(num=os.path.basename(filename))
    plt.plot(icj["Infected"].data)
    plt.title("Infected Over Time from InsetChart Channel")
    plt.xlabel("Time Step")
    plt.ylabel("#Infected")
    plt.show()

    df = icj.as_dataframe()
    plt.subplots(num=os.path.basename(filename))
    plt.semilogy(df["Susceptible Population"])
    plt.semilogy(df["Exposed Population"])
    plt.semilogy(df["Infectious Population"])
    plt.semilogy(df["Recovered Population"])
    plt.title("SEIR Channels from Data Frame")
    plt.xlabel("Time Step")
    plt.ylabel("Fraction of Population")
    plt.legend(["Susceptible", "Exposed", "Infectious", "Recovered"], loc="right")
    plt.show()

    return


def dump_source():

    with open(SCRIPT_PATH, "r") as file:
        print(file.read())

    return


if __name__ == "__main__":
    parser = ArgumentParser()
    default = os.path.join(
        WORKING_DIRECTORY, "..", "tests", "data", "insetcharts", "InsetChart.json"
    )
    parser.add_argument(
        "-f", "--filename", type=str, default=default, help="inset chart filename"
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
    elif MATPLOTLIB and PANDAS:
        main(args.filename)
