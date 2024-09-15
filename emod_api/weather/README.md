# Weather (Climate)

This submodule provides scripts for creating (and reading) weather input files that are directly ingested by the DTK (EMOD). These files set the temperature, rainfall, and humidity for those models that use such data. Going forward, all reading and writing of these weather control files should be done via this submodule. This submodule is shared between MSE and DSE.

### Getting Started

```python
from emod_api.weather.weather import Weather, WeatherNode
```

### Tutorials

<details><summary><b>Loading an Existing Binary File</b></summary>

Pass a valid filename to Weather, ```Weather(filename)```, to create a Weather object from an existing file. The filename should reference the .bin file, e.g., _airtemp.bin_. The associated metadata file, e.g., _airtemp.bin.json_, must exist in the same directory.

```python
weatherFile = Weather('airtemp.bin')
```
</details>

<details><summary><b>Creating a File from Scratch</b></summary>

Start with a new Weather object initialized with appropriate metadata. At a minimum you must supply the node IDs and the number of data values for each node.

Optionally set any of the other components of the metadata:

* author [Author] (author=_current user_)
* created [DateCreated] (default=datetime.now())
* frequency [UpdateResolution] (default='CLIMATE_UPDATE_DAY')
* provenance [DataProvenance] (default='unknown')
* reference [IdReference] (default='Legacy')

```python
nodeIds = [1, 3, 5, 7, 11, 13]
weather = Weather(nodeIds, 365)
```

Set the data for each node:

```python
for nodeId, node in weather.nodes.items():
    node[:] = data_for_node_nodeId
```

Write the data to a file (and metadata file) given the filename (writes _filename_ and _filename_.json):

```python
weather.write_file(filename)
```

</details>

<details><summary><b>Creating a File from a Comma Separated Value (CSV) File</b></summary>

Load the file with `Weather.fromCsv(filename)` and inspect and/or create a DTK compatible file:

```python
weather = Weather.from_csv('filename.csv')
# optionally inspect and/or modify data here
weather.write_file('filename.bin') # creates filename.bin and filename.bin.json for use with the DTK
```
</details>

### Sample Projects

### API Reference

<details><summary><b>Weather</b></summary>

```python
Weather(filename=None,
        node_ids=None,
        datavalue_count=None,
        author=None,
        created=None,
        frequency=None,
        provenance=None,
        reference=None,
        data=None)
```  
  
Create a Weather object from the given file _**or**_ create a Weather object with the given metadata (see below) and, optionally, given data. ```data``` should be a numpy array with shape (#nodes, #values). If not reading a file, `node_ids` and `datavalue_count` are required parameters.

```Weather.data``` &#8594; reference to the underlying weather data. This is a numpy array with shape (#nodes, #values).

```Weather.author``` &#8594; string

```Weather.creation_date``` &#8594; datetime

```Weather.datavalue_count``` &#8594; number of data values per node

```Weather.id_reference``` &#8594; string

```Weather.node_count``` &#8594;

```Weather.node_ids``` &#8594; list of node IDs

```Weather.provenance``` &#8594; string

```Weather.update_resolution``` &#8594; string

```Weather.nodes``` &#8594; dictionary of nodeId:WeatherNodes (see below).

```Weather[nodeId]``` &#8594; WeatherNode (see below) based on given node ID.

```Weather.write_file(filename)```  Writes the weather data to _`filename`_ and the metadata to _`filename.json`_.

```
Weather.from_csv(
    filename,
    var_column='airtemp',
    id_column='node_id',
    step_column='step',
    author=None,
    provenance=None
```

This static method reads the data from _`filename`_ and returns a Weather object. By default, the CSV file should contain the columns `airtemp`, `node_id`, and `step` to indicate the source columns. Any or all of these column names may be overridden to match the source CSV file schema. E.g., given the following CSV:

```csv
day,rain,node
1,12,12345678
2,10,12345678
3,13,12345678
...
```

The appropriate `from_csv()` call would be
```python
w = Weather.from_csv('filename.csv', var_column='rain', id_column='node', step='day')
```
</details>

<details><summary><b>WeatherNode</b></summary>

```WeatherNode(node_id, data)``` _Not for public use._

```WeatherNode.id``` &#8594; node ID (integer).

```WeatherNode.data``` &#8594; time series data (float32).

```WeatherNode[index]```  
R/W access to time series data for this node. 0 &#8804; index < metadata.datavalueCount. Slicing, e.g., `node[31:59]` is supported. 
</details>

### Architecture Documentation

Data for the Weather object is held as a numpy array with shape (#nodes, #values). This can be read/written directly from the binary file.  

Each WeatherNode contains a "view" into the appropriate portion of the full array. This means that `node.data` is read only.  

Updating node data requires using `node.data[index]`  or `node[index]` syntax. Bulk update of node data can be accomplished with `node.data[:] = new_data` or  `node[:] = new_data`.

### Other

To test the submodule:  

```bash
python -m emod_api.tests.weather_files
```

To run the example:

```bash
python -m emod_api.examples.weather_file
    [-f|--file filename ('test/Kenya_Nairobi_2.5arcmin_air_temperature_daily.bin')]
    [-d|--day # (180)]
    [-m|--map colormap ('RdYlBu_r')]
    [-n|--min min_scale (0.0)]
    [-x|--max max_scale (60.0)]
```