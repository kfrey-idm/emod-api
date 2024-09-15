import json
import tempfile
import os

import emod_api.schema.get_schema as get_schema
import emod_api.config.default_from_schema as default
import emod_api.schema_to_class as s2c

schema_path = None

def _make_config( eradication_path ):
    """
    This function uses emod_api to produce a guaranteed working config starting with an Eradication binary
    and a parameters-of-interest python file. This is really sample code, not a function you can invoke 
    as there is likely no poi file in the module.
    """
    import poi

    get_schema.dtk_to_schema(eradication_path, "/var/tmp/schema.json")
    default.write_default_from_schema("/var/tmp/schema.json")
    config = json.load(open("default_config.json"), object_hook=s2c.ReadOnlyDict)
    config = poi.set_params(config)
    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4, sort_keys=True)
    return "config.json"

def schema_to_config( schema_path_in ):
    """
    Purpose: Take a schema.json and return a "smart" config object that can be assigned 
    to with schema-enforcement. Use in conjunction with to_file().
    Params: schema_path_in (str/path)
    Returns: config (smart dict)
    """
    default.write_default_from_schema( schema_path_in )
    config = json.load(open("default_config.json"), object_hook=s2c.ReadOnlyDict)
    os.remove( "default_config.json" )
    return config

def set_schema( schema_path_in ):
    schema_path = schema_path_in 

def make_config_from_poi_and_config_dict( start_config_dict, poi_set_param_fn ):
    """
    Use this function to create a config.json from an existing param dict (defaults or base) and a function with 
    your parameter overrides or parameters of interest.
    """
    # OK, starting_config_dict is now a ReadOnlyDict that can do schema checks if it has a schema.
    # This is big TBD especially for config. And depends-on.
    starting_config_dict.set_schema( schema_path ) # set a path, or a dict? Need a superset config with per-param schema blobs.

    config = poi_set_param_fn(start_config_dict)
    with open("config.json", "w") as config_file:
        json.dump(config, config_file, indent=4, sort_keys=True)
    print( "config.json file written to disk." )
    return "config.json"

def make_config_from_poi_and_config_file( start_config_path, poi_set_param_fn ):
    """
    Use this function to create a config.json from an existing config json file (defaults or base) and a function with 
    your parameter overrides or parameters of interest.
    """
    if not os.path.exists( start_config_path ):
        print( f"{start_config_path} not found by {__file__}." )
        return None
    config = json.load(open(start_config_path), object_hook=s2c.ReadOnlyDict)
    return make_config_from_poi_and_config_dict( config, poi_set_param_fn )

def make_config_from_poi_and_schema( schema_path, poi_set_param_fn ):
    """
    Use this function to create a config.json from an existing schema json file and a function with 
    your parameter overrides or parameters of interest.
    """
    default.write_default_from_schema( schema_path )
    return make_config_from_poi_and_config_file( "default_config.json", poi_set_param_fn )

def make_config_from_poi( eradication_path, poi_set_param_fn ):
    """
    This function uses emod_api to produce a guaranteed working config starting with an Eradication 
    binary and a parameters-of-interest python function. This is a usable and useful function.

    Parameters:
        eradication_path (string): Fully-qualified path to Eradication binary that can be invoked to get a schema.
        poi_set_param_fn (function): User-provided function/callback/hook that looks like:

        def set_params( config ):
            config.parameters.<param_name> = <schema valid param_value>
            <repeat for each param>
            return config

    Returns:
        "config.json" (string): Hardcoded configuration filename written to pwd.
    """ 
    tmpdir = tempfile.mkdtemp()
    schema_path = os.path.join( tmpdir, "schema.json" )
    get_schema.dtk_to_schema(eradication_path, schema_path )
    return make_config_from_poi_and_schema( schema_path, poi_set_param_fn )
