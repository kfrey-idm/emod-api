# Serialization

These files contain functions to read and write (compressed) serialized population files (*.dtk).

```
import json
import emod_api.serialization.SerializedPopulation as SerPop
pop = SerPop.SerializedPopulation( /path/to/file.dtk )
print( json.dumps( pop.nodes, sort_keys=True, indent=4 ) )

```


