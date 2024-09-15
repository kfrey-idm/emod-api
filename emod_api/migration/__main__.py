#! /usr/bin/env python3

from argparse import ArgumentParser
from pathlib import Path
import sys

from .migration import to_csv, examine_file


if __name__ == "__main__":
    parser = ArgumentParser(prog='migration')
    parser.add_argument("-c", "--csv", type=Path, default=None,
                        help="Dump contents of <filename> to stdout in CSV format.", metavar='<filename>')
    parser.add_argument("-e", "--examine", type=Path, default=None, help="Display metadata from <filename> on stdout.",
                        metavar='<filename>')
    args = parser.parse_args()

    if len(sys.argv) > 1:
        to_csv(args.csv) if args.csv else None
        examine_file(args.examine) if args.examine else None
    else:
        parser.print_help()
