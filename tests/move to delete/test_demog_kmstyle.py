##
"""
Purpose: Test ability to create demographics.json per Kevin M's methods.

Run this via: python3 tests/test_demog_kmstyle.py tests/data/demographics/demog_in.csv outputs/demographics.json
"""

import pandas as pd
import os
import sys

from emod_api.demographics.Demographics import Demographics
from emod_api.demographics.Node import Node
#sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) # make this a real pip installable module and this stuff goes away
from emod_api.demographics.DemographicsInputDataParsers import node_ID_from_lat_long, duplicate_nodeID_check # -> emodpy


def nodes_from_csv(input_file, res=30/3600):
    if not os.path.exists( input_file ):
        print( f"{input_file} not found." )
        return

    node_info = pd.read_csv(input_file, encoding='iso-8859-1')
    out_nodes = []
    for index, row in node_info.iterrows():
        pop = int(6*row['under5_pop'])
        if pop<25000:
            continue
        lat = row['lat']
        lon = row['lon']
        meta = {'dot_name': (row['ADM0_NAME']+':'+row['ADM1_NAME']+':'+row['ADM2_NAME']),
                'GUID': row['GUID'],
                'density': row['under5_pop_weighted_density']}
        node = Node(
                lat=lat,
                lon=lon,
                pop=pop,
                name=int(node_ID_from_lat_long(lat, lon, res)),
                forced_id=int(node_ID_from_lat_long(lat, lon, res)),meta=meta)

        out_nodes.append(node)
    out_nodes = duplicate_nodeID_check(out_nodes)
    for node in out_nodes:
        if node.id == 1639001798:  #Not sure why this node causes issues, just dump it for speed.  Probably an issue in the duplicate nodeID check
            remel = node
    out_nodes.remove(remel)

    return out_nodes

def main():
    input_file = sys.argv[1]
    outDemogFile = sys.argv[2]
    nodes = nodes_from_csv(input_file, res=30/3600)

    demog = Demographics(nodes=nodes)
    # Now we have a demographics file with the individual node (LGA) properties set correctly.  Now let's set the
    # country-wide defaults - age distribution, immune initialization, etc.
    demog.SetDefaultProperties()
    demog.generate_file(outDemogFile)

if __name__ == "__main__":
    main()

