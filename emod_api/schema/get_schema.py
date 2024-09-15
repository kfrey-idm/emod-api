import subprocess
import sys
import os
import pathlib
from emod_api.schema import dtk_post_process_schema as dpps

def dtk_to_schema( path_to_binary, path_to_write_schema="schema.json" ):
    """
    Runs /path/to/Eradication --get-schema --schema-path=schema.json and then post-processes the schema into something more useful.
    Error cases handled:
    - schema.json file already exists in cwd; does not overwrite. Asks users to move and retry.
    - Specified binary fails to run to completion.
    - Specified binary fails to produce a schema.json
    """
    # Get folder (not file) and create if does not exist.
    target_dir = pathlib.Path( path_to_write_schema ).parent
    if target_dir.exists() == False:
        target_dir.mkdir()
    if os.path.exists( path_to_write_schema ):
        print( f"WARNING: {path_to_write_schema} already exists. Overwriting." )
    try:
        subprocess.call( [ path_to_binary, "--get-schema", "--schema-path", path_to_write_schema ], stdout=open(os.devnull) )
    except Exception as ex:
        print( "Something bad happened while trying to run the Eradication binary." )
        print( str( ex ) )
        sys.exit()
    if os.path.exists( path_to_write_schema ) == False:
        print( f"The specified EMOD executable failed to write {path_to_write_schema}." )
        sys.exit()
    dpps.application( path_to_write_schema )
    print( f"Wrote {path_to_write_schema} file." )

if __name__ == "__main__":
    if len( sys.argv ) == 1:
        print( "Please specify path to Eradication binary/exe." )
    else:
        dtk_to_schema( sys.argv[1] )
