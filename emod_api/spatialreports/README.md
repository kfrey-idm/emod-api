# SpatialOutput

This submodule provides scripts for interacting with binary formatted spatial output files produced by the DTK (EMOD). 

### Getting Started

```python
from emod_api.spatialreports.spatial import SpatialReport, SpatialNode
```

### Tutorials

#### Loading an Existing Spatial Report

Pass a valid filename to SpatialReport, ```SpatialReport(filename)```, to create a SpatialReport object from an existing file. Then access the data for each, any, or all nodes by node ID[s].

```python
from emod_api.spatialreports.spatial import SpatialReport

report = SpatialReport('SpatialReport_Prevalence.bin')
node_id = report.node_ids[0] # pick a valid node ID
time_step = 180
print(f'Value for node {node_id} at time step {time_step} is {report.nodes[node_id][time_step]}')
sum = 0.0
for node_id, node in report.nodes.items():
    sum += node[time_step]
mean = sum / len(report.nodes)
print(f'Mean across all nodes at time {time_step} is {mean}.')
```

### Sample Projects

### API Reference

<details><summary><b>SpatialReport</b></summary>

```python
SpatialReport(filename=None, node_ids=None, data=None)
```
Create a SpatialReport object from the given filename _**or**_
create a SpatialReport object with the given node IDs and initial data.  
`node_ids` should be a non-empty iterable of unique integers.  
`data` should be a numpy float32 array with shape (#values, #nodes).  

If reading from a file, the file should have the following structure:  

```text
1 x uint32                  // number of nodes
1 x uint32                  // number of data values/time steps
#nodes x uint32             // node IDs
(#nodes x uint32) x #values // report data
```
[reference](http://www.idmod.org/docs/general/software-report-spatial.html)


```SpatialReport.data``` &#8594; reference to the underlying report data. This is a numpy float32 array with shape (#values, #nodes).

```SpatialReport.node_ids``` &#8594; list of node IDs.

```SpatialReport.nodes``` &#8594; dictionary of nodeId:SpatialNodes (see below).

```SpatialReport[node_id]``` &#8594; SpatialNode (see below) based on given node ID.

```SpatialReport.node_count``` &#8594; number of nodes in the report.

```SpatialReport.time_steps``` &#8594; number of data values for each node.

```SpatialReport.write_file(filename)``` Writes the report data to _`filename`_.
</details>

<details><summary><b>SpatialNode</b></summary>

```SpatialNode(node_id, data)``` _Not for public use._

```SpatialNode.id``` &#8594; node ID (integer)

```SpatialNode.data``` &#8594; time series data (float32)

```SpatialNode[index]``` R/W access to time series data. 0 &#8804; index < report.timeSteps. Slices, e.g., `node[31:59]`, supported.
</details>

### Architecture Documentation

Data for the SpatialReport object is held as a numpy array with shape (#values, #nodes). This can be read/written directly from the binary file.  

Each SpatialNode contains a "view" into the appropriate portion of the full array. This means that `node.data` is read only.  

Updating node data requires using `node.data[index]`  or `node[index]` syntax. Bulk update of node data can be accomplished with `node.data[:] = new_data` or  `node[:] = new_data`.


### Other

To test the submodule:  
```bash
python -m emod_api.tests.spatial_reports
```

To run the example:
```bash
python -m emod_api.examples.spatial_report
```
