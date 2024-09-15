import emod_api.config.default_from_schema_no_validation as dfs

dfs.write_default_from_schema( "schema.json" )
dfs.write_default_from_schema( "schema.json", False )
