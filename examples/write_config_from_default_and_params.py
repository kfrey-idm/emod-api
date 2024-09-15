#!/usr/bin/python

import emod_api.config.default_from_schema_no_validation as dfs
import some_config_i_found
import os
import sys

# binary -> schema
if not os.path.exists( "schema.json" ):
    print( """Do: 
            \tpython -m emod_api.schema.get_schema /path/to/Eradication
            """ )
    sys.exit()

# schema -> default config
default_config = dfs.write_default_from_schema( "schema.json" )

# default and my params -> my_config
dfs.write_config_from_default_and_params( default_config, some_config_i_found.set, "new_config.json" )
