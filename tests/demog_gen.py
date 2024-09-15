#!/usr/bin/env python
"""
The purpose of this script is to exercise DemographicsGenerator and DemographicsFile as the primary way to 
create demographics json files for use in DTK from input data (of various formats) and with various options.
Usage is 3 step:
    1) Read/parse/ingest population data by node (and represent as Python objects)
    2) Set/assign/manipulate the default values and distributions 3) Write/dump to disk

One possible way to run this is:
    python3 tests/test_demog_gen.py tests/data/addis_geometries_full_pop_grid.csv outputs/spatial_75_demographics.json 
"""

import sys # I'm sure I'll use argparse later but not adding dependencies until they are needed
from emod_api.demographics import DemographicsGenerator
#from emod_api.demographics import DemographicsFile

# This function actually does All The Things, which is lame
DemographicsGenerator.from_file(
        population_input_file=sys.argv[1],
        demographics_filename=sys.argv[2]
    )
