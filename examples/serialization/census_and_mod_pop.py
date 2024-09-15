#!/usr/bin/env python

import sys
import random
import emod_api.serialization.CensusAndModPop as CAMP

def non_modifier_fn( individual ):
    """
    This version of the function obviously doesn't modify anything. It just prints to console.
    """
    # print( individual )
    print( f'individual {individual["suid"]["id"]} is {individual["m_age"]} days old.' )
    return individual

def modifier_fn( individual ):
    """
    Let'take half the women and give them a random age from 0 to 100. Just because.
    """
    if random.random() < 0.5 and individual["m_gender"] == 1:
        # print( "Assigning age." )
        individual["m_age"] = random.random() * 365000
    return individual

if __name__ == "__main__":
    if len( sys.argv ) < 1:
        print( f"USAGE: {sys.argv[0]} <serialized_population_file>" )
        sys.exit(0)
    CAMP.change_ser_pop( sys.argv[1], non_modifier_fn, "new_ser_pop.dtk" )
    CAMP.change_ser_pop( sys.argv[1], modifier_fn, "new_ser_pop.dtk" )
    CAMP.change_ser_pop( "new_ser_pop.dtk", non_modifier_fn, "new_ser_pop.dtk" )
