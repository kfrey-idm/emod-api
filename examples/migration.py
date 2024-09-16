#! /usr/bin/env python3

from argparse import ArgumentParser
import sys
from collections import namedtuple
from pathlib import Path

import emod_api.migration as migration  # for from_file()
from emod_api.migration import Migration


def main(options):

    if options.basic:
        create_basic_migration_file()

    if options.age:
        create_age_dependent_migration_file()

    if options.gender:
        create_gender_dependent_migration_file()

    if options.both:
        create_age_and_gender_dependent_migration_file()

    if options.examine:
        examine_migration_file(options.examine)

    if options.from_csv:
        create_migration_file_from_csv()

    return


def create_basic_migration_file():

    nodes = _get_nxn_nodes(5)

    # Create a migration file with all the defaults. Primarily:
    # no age dependency, no gender dependency, IdReference = "Legacy", migration type = LOCAL_MIGRATION
    migration_data = Migration()

    # For all pairs of nodes, migration rate is 0.1 / Manhattan distance
    for source_id, source in nodes.items():
        for dest_id, dest in nodes.items():
            if dest_id != source_id:
                distance = abs(dest.x-source.x) + abs(dest.y-source.y)
                rate = 0.1 / distance
                migration_data[source_id][dest_id] = rate

    print(f"Created migration at {migration_data.DateCreated:%a %B %d %Y %H:%M}")
    print(f"Created migration with {migration_data.NodeCount} nodes.")
    print(f"Created migration with {migration_data.DatavalueCount} destinations per node.")

    migration_data.to_file(Path("basic_local_migration.bin"))

    return


def _get_nxn_nodes(size: int = 5) -> dict:

    Center = namedtuple("Center", ["x", "y"])

    # NxN grid, distance between nodes is just Manhattan distance
    locations = []
    for y in range(size):
        for x in range(size):
            locations.append(Center(x, y))

    # map nodes to their location, index will be used for node_id
    nodes = {index: location for index, location in enumerate(locations)}

    return nodes


def create_age_dependent_migration_file():

    migration_data = Migration()
    migration_data.AgesYears = [10, 60, 125]

    factors = {10: 0.8, 60: 1.0, 125: 0.67}

    nodes = _get_nxn_nodes(5)
    for source_id, source in nodes.items():
        for dest_id, dest in nodes.items():
            if dest_id != source_id:
                distance = abs(dest.x-source.x) + abs(dest.y-source.y)
                rate = 0.1 / distance
                for age in migration_data.AgesYears:
                    migration_data[source_id:age][dest_id] = factors[age] * rate

    print(f"Created migration at {migration_data.DateCreated:%a %B %d %Y %H:%M}")
    print(f"Migration rate from 0 -> 1 [ 0- 10] = {migration_data[0:5][1]:.4}")
    print(f"Migration rate from 0 -> 1 (10- 60] = {migration_data[0,40][1]:.4}")
    print(f"Migration rate from 0 -> 1 (60-125) = {migration_data[0:75][1]:.4}")

    # migration_data.to_file(Path("age_dependent_local_migration.bin"))

    return


def create_gender_dependent_migration_file():

    migration_data = Migration()
    migration_data.GenderDataType = Migration.ONE_FOR_EACH_GENDER

    factors = {Migration.MALE: 1.2, Migration.FEMALE: 0.8}

    nodes = _get_nxn_nodes(5)
    for source_id, source in nodes.items():
        for dest_id, dest in nodes.items():
            if dest_id != source_id:
                distance = abs(dest.x-source.x) + abs(dest.y-source.y)
                rate = 0.1 / distance
                for gender, factor in factors.items():
                    migration_data[source_id:gender][dest_id] = factor * rate

    print(f"Created migration at {migration_data.DateCreated:%a %B %d %Y %H:%M}")
    print(f"Migration rate from 0 -> 1 ( male ) = {migration_data[0:Migration.MALE][1]:.4}")
    print(f"Migration rate from 0 -> 1 (female) = {migration_data[0:Migration.FEMALE][1]:.4}")

    # migration_data.to_file(Path("gender_dependent_local_migration.bin"))

    return


def create_age_and_gender_dependent_migration_file():

    migration_data = Migration()
    age_factors = {10: 0.8, 60: 1.0, 125: 0.67}
    gender_factors = {Migration.MALE: 1.2, Migration.FEMALE: 0.8}
    migration_data.AgesYears = sorted(age_factors.keys())
    migration_data.GenderDataType = Migration.ONE_FOR_EACH_GENDER

    nodes = _get_nxn_nodes(5)
    for source_id, source in nodes.items():
        for dest_id, dest in nodes.items():
            if dest_id != source_id:
                distance = abs(dest.x-source.x) + abs(dest.y-source.y)
                rate = 0.1 / distance
                for gender, kg in gender_factors.items():
                    for age, ka in age_factors.items():
                        migration_data[source_id:gender:age][dest_id] = kg * ka * rate

    print(f"Created migration at {migration_data.DateCreated:%a %B %d %Y %H:%M}")
    print(f"Migration rate from 0 -> 1 ( male,   5yo) = {migration_data[0:Migration.MALE:5][1]:.4}")
    print(f"Migration rate from 0 -> 1 ( male,  25yo) = {migration_data[0,Migration.MALE,25][1]:.4}")
    print(f"Migration rate from 0 -> 1 (female, 25yo) = {migration_data[0:Migration.FEMALE:25][1]:.4}")
    print(f"Migration rate from 0 -> 1 (female, 75yo) = {migration_data[0,Migration.FEMALE,75][1]:.4}")

    # migration_data.to_file(Path("age_and_gender_dependent_local_migration.bin"))

    return


def examine_migration_file(filename):

    migration_file = migration.from_file(filename)
    print(f"Author:            {migration_file.Author}")
    print(f"DatavalueCount:    {migration_file.DatavalueCount}")
    print(f"DateCreated:       {migration_file.DateCreated:%a %B %d %Y %H:%M}")
    print(f"GenderDataType:    {migration_file.GenderDataType}")
    print(f"IdReference:       {migration_file.IdReference}")
    print(f"InterpolationType: {migration_file.InterpolationType}")
    print(f"MigrationType:     {migration_file.MigrationType}")
    print(f"NodeCount:         {migration_file.NodeCount}")
    print(f"NodeOffsets:       {migration_file.NodeOffsets}")
    print(f"Tool:              {migration_file.Tool}")
    print(f"Nodes:             {migration_file.Nodes}")

    nodes = migration_file.Nodes
    a = nodes[0]
    b = nodes[-1]
    print(f"Rate from {a} to {b} is {migration_file[a][b] if b in migration_file[a] else 0}")
    print(f"Rate from {b} to {a} is {migration_file[b][a] if a in migration_file[b] else 0}")

    # convert to regional migration
    migration_file.MigrationType = "REGIONAL_MIGRATION"
    migration_file.MigrationType = Migration.REGIONAL
    migration_file.InterpolationType = Migration.LINEAR_INTERPOLATION
    # migration_data.to_file(Path("regional_migration.bin"))

    return


def create_migration_file_from_csv():
    """
        Creates migration object using from_csv() function and writes out migration file consumable by EMOD
        using to_file() function.

    Returns:
        Nothing
    """
    # filename - path to the csv file you're converting to EMOD-consumable migration file
    # the csv file needs to have headings of "source", "destination", and "rate"
    # with "source" and "destination" being NodeIDs from the demographics file you'll be using with the migration files

    # id_ref - sets the IdReference metadata parameter. It needs to match the IdReference metadata parameter
    # in your demographics file, otherwise simulation will not run.

    # mig_type - sets the MigrationType metadata parameter, use the Migration enum parameters to set
    #     "LOCAL_MIGRATION": LOCAL
    #     "AIR_MIGRATION": AIR
    #     "REGIONAL_MIGRATION": REGIONAL
    #     "SEA_MIGRATION": SEA
    #     "FAMILY_MIGRATION": FAMILY
    #     "INTERVENTION_MIGRATION": INTERVENTION
    # or ints 1-6 respectively

    migration_type = Migration.SEA
    migration_object = migration.from_csv(filename=Path("migration_csv_example.csv"),
                                          id_ref="Gridded world grump2.5arcmin",
                                          mig_type=migration_type)

    # binaryfile - path and name that will become the name and location of the migration file.

    # metafile - path that will become the name and location of the meta information file for the migration file.
    # they should be in the same folder and be named the same (+.json extension). Best to leave this blank.
    # It will be automatically created for you

    # value_limit - limit on number of destination values to write for each source node (default = 100)

    migration_object.to_file(binaryfile=r"..\lake_walk_file",
                             # Path("lake_walk_file") also works for the same location folder
                             metafile=None, value_limit=15)

    return

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-b", "--basic", action="store_true", help="create a basic migration file")
    parser.add_argument("-a", "--age", action="store_true", help="create a migration file with age dependency")
    parser.add_argument("-g", "--gender", action="store_true", help="create a migration file with gender dependency")
    parser.add_argument("--both", action="store_true", help="create a migration file with both age and gender dependency")
    parser.add_argument("-e", "--examine", type=Path, help="display metadata for the given file")
    parser.add_argument("-c", "--from_csv", action="store_true", help="create migration file from csv file")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        print( "You need to specify one of the arguments. Run -h to see help." )
    else:
        main(args)
