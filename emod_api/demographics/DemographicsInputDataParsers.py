#!/usr/bin/env python

"""
This file contains functions used to read, parse, and process input data files and convert the
data into Nodes. Plus utility support function that are part of that process.
There is no fixed fileformat for the incoming data. Any file format that is supported by a function
here is a supported format. You can add to this.
"""
import numpy as np
import pandas as pd # might be a bit of a heavy dependency for what it's used for here.
from copy import deepcopy
from emod_api.demographics.Node import Node

# The below implements the standard naming convention for DTK nodes based on latitude and longitude.
# The node ID encodes both lat and long at a specified pixel resolution, and I've maintained this 
# convention even when running on spatial setups that are not non-uniform grids.
def node_ID_from_lat_long(lat, long, res=30/3600):
    nodeID = int((np.floor((long+180)/res)*(2**16)).astype(np.uint) + (np.floor((lat+90)/res)+1).astype(np.uint))
    return nodeID


def duplicate_nodeID_check(nodelist):
    nodeIDs = pd.Series([n.id for n in nodelist])
    dups = nodeIDs.duplicated()
    while any(dups):
        # In lieu of something more clever, find the first non-unique, find a nearby unused ID,
        # and loop until all IDs are unique
        ind2fix = dups[dups].index[0]
        oldNodeID = nodeIDs[ind2fix]
        newNodeID = oldNodeID
        shift = 0
        while newNodeID == oldNodeID:
            shift += 1
            for xs in range(-1*shift, shift):
                for ys in range(-1*shift, shift):
                    testId = oldNodeID + xs*2**16 + ys
                    if not any(nodeIDs.isin([testId])):
                        newNodeID = testId
        nodeIDs[ind2fix] = newNodeID
        # nodelist[ind2fix]['NodeID'] = int(newNodeID)
        n = deepcopy(nodelist[ind2fix])

        nodelist[ind2fix] = Node(n.node_attributes.latitude,
                                 n.node_attributes.longitude,
                                 n.node_attributes.initial_population,
                                 forced_id=int(newNodeID),
                                 node_attributes=n.node_attributes)
        dups = nodeIDs.duplicated()
    return nodelist


def fill_nodes_legacy(node_info, DemoDf, res=30/3600):
    out_nodes = []
    for index, row in node_info.iterrows():
        pop = int(1000*row['population'])
        lat = row['latitude']
        lon = row['longitude']
        extra_attributes = {'Area_deg2': row['area'], 'Area_km2': row['area']*111*111}
        meta = {'dot_name': row['dot_name']}

        if (pop / extra_attributes['Area_km2']) > 1500:
            extra_attributes['Urban'] = 1
        else:
            extra_attributes['Urban'] = 0

        state = row['dot_name'].split(':')[1]
        BirthRate = math.log(1+DemoDf['CBR'][state] / 1000)/365
        extra_attributes.update({'BirthRate': BirthRate })

        MortAndAgeDist, BRScalars, GrowthRates = MortalityAndAgeDistributions(row['dot_name'], DemoDf, BirthRate)
        meta.update({'IndividualAttributes': MortAndAgeDist})
 #      Node-level individual properties can be set here, though I am going to do this
 #      instead using a PropertyChanger intervention delivered on birth, as that will
#       make it easier later when coverage needs to scale up over time.
#       Will however, record the node-level RI rates to make campaign file building easier
 #       meta.update({'IndividualProperties': {"Property": "Accessibility",
 #           "Values": ["MCV2","MCV1","SIAOnly"],
 #           "Initial_Distribution": [0.0,row['birthAveragedRI'],1.0-row['birthAveragedRI'] ] } } )
        #Record metadata on routine immunization rates, computed population growth rate tested at different birth rates.
        meta.update({'META_RIrate': row['birthAveragedRI']})
        meta.update({'META_TestBRScalars': BRScalars})
        meta.update({'META_Growthrate': GrowthRates})

        node = Node(lat=lat, lon=lon, pop=pop, name=int(node_ID_from_lat_long(lat, lon, res)),
                        forced_id=int(node_ID_from_lat_long(lat, lon, res)),
                        extra_attributes=extra_attributes, meta=meta)

        out_nodes.append(node)
    out_nodes = duplicate_nodeID_check(out_nodes)
    return out_nodes

def ConstructNodesFromDataFrame(node_info, extra_data_columns = [], res=30/3600):

    # Requirements: each row of the node_info dataframe represents a node for simulation.
    # The dataframe must have columns labeled population, latitude, and longitude.
    # extra_data_columns is a list of strings, signifying extra columns to be added to the "NodeAttributes" field of the node;
    # this can include functional fields (e.g., "Urban", "BirthRate") or metadata fields (e.g., "dot_name").  The name
    # of extra columns will be copied directly as the key name inside of the NodeAttributes dict.
    # If you want to add individual attributes (mortality distributions, for example) to a node, these should be added
    # after construction.  If this whole builder were a class, resolution would be available and not have to be passed.

    out_nodes = []

    for index, row in node_info.iterrows():
        # By default, set node ID using lat long.  Should we allow a node ID field to be in the dataframe, instead?
        if 'nodeID' in row.index:
            ID = int(row['nodeID'])
        else:
            ID = int(node_ID_from_lat_long(row['latitude'], row['longitude'], res))

        out_nodes.append(
            Node(lat=row['latitude'],
                 lon=row['longitude'],
                 pop=int(row['population']),     #Make sure population is in 1:1 units, not in 100s, 1000s, etc.
                 name=ID,                        #Not clear to me whether name or forced ID is the one to set, using both.
                 forced_id=ID,
                 extra_attributes={col: row[col] for col in extra_data_columns})
        )

    out_nodes = duplicate_nodeID_check(out_nodes)   #If nodes are very close together, they may get the same ID!  Correct for this.
    return out_nodes


