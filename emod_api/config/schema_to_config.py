from emod_api.config import from_schema as old

class SchemaConfigBuilder(old.SchemaConfigBuilder): 
    """
    Deprecated in API v.1.
    Supported temporarily as pass-through functionality to emod_api.config.from_schema.
    """
    print( "emod_api.config.schema_to_config is deprecated. Please use emod_api.config.from_schema." )
    pass

if __name__ == "__main__":

    print( "emod_api.config.schema_to_config is deprecated. Please use emod_api.config.from_schema." )
    old._do_main()
