import argparse
import gc
import json

# from dtk.tools.serialization.idtkFileTools import read_idtk_file
from emod_api.dtk_tools.serialization.idtkFileTools import read_idtk_file

"""
This script will take serialization files dumped from a multi-core job
and merge them into a valid file for single-core initialization
"""


def serialized_dtk_to_json(filename_format, core_idx=0):
    filename = filename_format % core_idx
    print("\n%s\nReading: %s\n%s\n" % ("-" * 30, filename, "-" * 30))
    header, payload, contents, data = read_idtk_file(filename)
    # print(header)
    # TODO: memory cleanup?
    del payload
    del contents
    suid_keys = [k for k in data["simulation"].keys() if "SuidGenerator" in k]
    for suid_key in suid_keys:
        print("\n%s" % suid_key)
        print("  Setting %s.numtasks to 1" % suid_key)
        data["simulation"][suid_key]["numtasks"] = 1
    print("\n%d nodes on rank %d" % (len(data["simulation"]["nodes"]), core_idx))
    # Merge other files into rank-0
    for core_idx in range(1, 24):

        filename = "state-00365-%03d.dtk" % core_idx
        print("\n%s\nReading: %s\n%s\n" % ("-" * 30, filename, "-" * 30))
        next_header, payload, contents, next_data = read_idtk_file(filename)
        del payload
        del contents

        print(gc.get_count())
        gc.collect()

        for suid_key in suid_keys:
            print("\n%s" % suid_key)
            next_suid_value = next_data["simulation"][suid_key]["next_suid"]["id"]
            max_suid_value = data["simulation"][suid_key]["next_suid"]["id"]
            if next_suid_value > max_suid_value:
                print("  Overwriting: %d > %d" % (next_suid_value, max_suid_value))
                data["simulation"][suid_key]["next_suid"]["id"] = next_suid_value
            else:
                print("  Keeping:  %d <= %d" % (next_suid_value, max_suid_value))

        data["simulation"]["nodes"] += next_data["simulation"]["nodes"]
        print(
            "\nAppended %d nodes from rank %d --> Total = %d"
            % (
                len(next_data["simulation"]["nodes"]),
                core_idx,
                len(data["simulation"]["nodes"]),
            )
        )

    return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script will take serialization files dumped from a multi-core "
        "job and merge them into a valid file for single-core initialization"
    )
    parser.add_argument(
        "--start-index",
        type=int,
        help="Which core index file to start with. Defaults to 0",
        default=0,
    )
    parser.add_argument(
        "core_filename_format_string",
        default="state-00365-%03d.dtk",
        help='File format string. For example: "state-00365-%%03d.dtk". The "%%03d" would be '
        "replaced with the core_index during reading",
    )

    parser.add_argument(
        "output-name",
        type=str,
        help="Output file name. For example: state-00365-merged.dtk",
    )
    args = parser.parse_args()

    data = serialized_dtk_to_json(args.core_filename_format_string, args.start_index)
    with open(args.output_name, "w") as fp:
        print("\n%s\nWriting: %s\n%s\n" % ("-" * 30, args.output_name, "-" * 30))
        json.dump(data, fp, indent=None, separators=(",", ":"))
